#!/usr/bin/env python3
"""NetDash — minik ağ gösterge paneli sunucusu.

SSD dostu tasarım:
  * Anlık hızlar /proc/net/dev'den okunur (RAM, disk IO yok).
  * Saatlik/günlük/aylık toplamlar vnstat'tan gelir (tek disk yazarı vnstat'tır).
  * Public IP günde 1 kez çekilir ve yalnızca bellekte tutulur.
  * HTTP access log yok; index.html açılışta belleğe alınır.
"""

import json
import socket
import subprocess
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

LAN_IFACES = ["enp0s31f6", "enp1s0"]
TS_IFACE = "tailscale0"
BIND = ("0.0.0.0", 8377)   # tum arayuzlerden erisilebilir; kimlik dogrulama yok

PUBIP_URLS = [
    "https://api.ipify.org",
    "https://icanhazip.com",
    "https://ifconfig.me/ip",
]
PUBIP_REFRESH = 24 * 3600   # günde 1
PUBIP_RETRY = 300           # hata olursa 5 dk sonra tekrar dene
VNSTAT_CACHE_TTL = 60       # vnstat --json en fazla dakikada 1 çağrılır

INDEX_HTML = (Path(__file__).parent / "index.html").read_bytes()

_state = {
    "public_ip": None,
    "public_ip_at": 0.0,
    "vnstat": None,
    "vnstat_at": 0.0,
}
_lock = threading.Lock()


# --------------------------------------------------------------------------
# Anlık sayaçlar (/proc/net/dev)

def read_counters():
    counters = {}
    with open("/proc/net/dev") as f:
        for line in f.readlines()[2:]:
            name, _, rest = line.partition(":")
            fields = rest.split()
            if len(fields) >= 9:
                counters[name.strip()] = (int(fields[0]), int(fields[8]))
    return counters


def iface_up(name):
    # tailscale0 gibi TUN arayuzleri operstate olarak 'unknown' doner (fiziksel
    # ethernet 'up'/'down' verir). Bu yuzden yalnizca 'down' pasif sayilir.
    try:
        with open(f"/sys/class/net/{name}/operstate") as f:
            return f.read().strip() != "down"
    except OSError:
        return False


def active_lan_iface():
    """Default route hangi LAN arayüzündeyse onu seç; yoksa 'up' olana düş."""
    try:
        with open("/proc/net/route") as f:
            best, best_metric = None, None
            for line in f.readlines()[1:]:
                p = line.split()
                if len(p) >= 7 and p[1] == "00000000" and int(p[3], 16) & 1:
                    metric = int(p[6])
                    if p[0] in LAN_IFACES and (best_metric is None or metric < best_metric):
                        best, best_metric = p[0], metric
            if best:
                return best
    except OSError:
        pass
    for name in LAN_IFACES:
        if iface_up(name):
            return name
    return LAN_IFACES[0]


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(("1.1.1.1", 80))  # paket gönderilmez, sadece route seçilir
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return None


# --------------------------------------------------------------------------
# Public IP (arka plan thread'i, yalnızca bellekte)

def _pubip_loop():
    while True:
        ip = None
        for url in PUBIP_URLS:
            try:
                with urllib.request.urlopen(url, timeout=8) as r:
                    text = r.read(64).decode().strip()
                if text and all(c in "0123456789.:abcdefABCDEF" for c in text):
                    ip = text
                    break
            except Exception:
                continue
        with _lock:
            if ip:
                _state["public_ip"] = ip
                _state["public_ip_at"] = time.time()
        time.sleep(PUBIP_REFRESH if ip else PUBIP_RETRY)


# --------------------------------------------------------------------------
# vnstat (bellek cache'li)

def _entry_key(e):
    d = e.get("date", {}) or {}
    t = e.get("time", {}) or {}
    return (d.get("year", 0), d.get("month", 0), d.get("day", 0),
            t.get("hour", -1), t.get("minute", t.get("minutes", 0)))


def _match(entries, keys):
    """vnstat girdilerinden şu anki döneme ait olanı bul; yoksa en yenisi."""
    now = time.localtime()
    want = {"year": now.tm_year, "month": now.tm_mon,
            "day": now.tm_mday, "hour": now.tm_hour}
    for e in entries:
        d = dict(e.get("date", {}))
        d.update(e.get("time", {}))
        if "hour" not in d and "hour" in keys and isinstance(e.get("id"), int):
            d["hour"] = e["id"]   # vnstat 1.x: saat bilgisi "id" alanindadir
        if all(d.get(k) == want[k] for k in keys):
            return e
    return max(entries, key=_entry_key) if entries else None


def _period(entry, scale):
    if not entry:
        return {"rx": 0, "tx": 0}
    return {"rx": entry.get("rx", 0) * scale, "tx": entry.get("tx", 0) * scale}


def vnstat_summary():
    now = time.monotonic()
    with _lock:
        if _state["vnstat"] and now - _state["vnstat_at"] < VNSTAT_CACHE_TTL:
            return _state["vnstat"]
    try:
        proc = subprocess.run(["vnstat", "--json"], capture_output=True,
                              timeout=15)
        if proc.returncode != 0:
            msg = (proc.stderr or proc.stdout or b"").decode(errors="replace").strip()
            return {"error": msg or "vnstat cikis kodu %d" % proc.returncode}
        data = json.loads(proc.stdout)
    except Exception as e:
        return {"error": str(e)}

    # vnstat 1.x: jsonversion "1", ad "id" alaninda, listeler hours/days/months,
    # degerler KiB. vnstat 2.x: jsonversion "2", ad "name", listeler tekil, bayt.
    v1 = str(data.get("jsonversion", "2")) == "1"
    scale = 1024 if v1 else 1

    result = {"updated": None, "ifaces": {}}
    for itf in data.get("interfaces", []):
        name = itf.get("name") or itf.get("id") or ""
        traffic = itf.get("traffic", {})
        upd = itf.get("updated", {})
        d, t = upd.get("date", {}), upd.get("time", {})
        if d:
            result["updated"] = "%04d-%02d-%02d %02d:%02d" % (
                d.get("year", 0), d.get("month", 0), d.get("day", 0),
                t.get("hour", 0), t.get("minute", t.get("minutes", 0)))
        result["ifaces"][name] = {
            "hour": _period(_match(traffic.get("hour") or traffic.get("hours") or [],
                                   ["year", "month", "day", "hour"]), scale),
            "day": _period(_match(traffic.get("day") or traffic.get("days") or [],
                                  ["year", "month", "day"]), scale),
            "month": _period(_match(traffic.get("month") or traffic.get("months") or [],
                                    ["year", "month"]), scale),
        }
    with _lock:
        _state["vnstat"] = result
        _state["vnstat_at"] = now
    return result


# --------------------------------------------------------------------------
# HTTP

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # access log yok -> disk/journal yazması yok
        pass

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj):
        self._send(200, json.dumps(obj).encode(), "application/json")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, INDEX_HTML, "text/html; charset=utf-8")
        elif self.path == "/api/live":
            lan = active_lan_iface()
            counters = read_counters()
            with _lock:
                pub = _state["public_ip"]
            self._json({
                "t": time.monotonic(),
                "hostname": socket.gethostname(),
                "local_ip": local_ip(),
                "public_ip": pub,
                "lan": {
                    "name": lan,
                    "up": iface_up(lan),
                    "rx": counters.get(lan, (0, 0))[0],
                    "tx": counters.get(lan, (0, 0))[1],
                },
                "ts": {
                    "name": TS_IFACE,
                    "up": TS_IFACE in counters and iface_up(TS_IFACE),
                    "rx": counters.get(TS_IFACE, (0, 0))[0],
                    "tx": counters.get(TS_IFACE, (0, 0))[1],
                },
            })
        elif self.path == "/api/vnstat":
            self._json(vnstat_summary())
        else:
            self._send(404, b"not found", "text/plain")


def main():
    threading.Thread(target=_pubip_loop, daemon=True).start()
    server = ThreadingHTTPServer(BIND, Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
