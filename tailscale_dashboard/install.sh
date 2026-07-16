#!/bin/bash
# NetDash kurulum betigi — Ubuntu uzerinde sudo ile calistirin:
#   sudo bash install.sh
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Lutfen sudo ile calistirin: sudo bash install.sh" >&2
  exit 1
fi

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST=/opt/netdash

echo "==> vnstat kuruluyor..."
apt-get update -qq
apt-get install -y -qq vnstat curl

echo "==> vnstat SSD dostu ayarlaniyor (SaveInterval 5 dk)..."
# Sayaclar RAM'de 20 sn'de bir guncellenir, diske 5 dk'da bir yazilir.
sed -i -E 's/^[;#]?[[:space:]]*SaveInterval[[:space:]].*/SaveInterval 5/' /etc/vnstat.conf
systemctl enable --now vnstat
sleep 2   # daemon veritabanini olustursun

echo "==> Izlenecek arayuzler vnstat'a ekleniyor..."
# Daemon calisirken root ile --add yapmak veritabani sahipligini bozabilir;
# once durdur, ekle, sahipligi duzelt, sonra baslat.
systemctl stop vnstat
for IFACE in enp0s31f6 enp1s0 tailscale0; do
  vnstat --add -i "$IFACE" 2>/dev/null || true
done
if id vnstat >/dev/null 2>&1; then
  chown -R vnstat:vnstat /var/lib/vnstat
fi
systemctl start vnstat

echo "==> Dosyalar $DEST altina kopyalaniyor..."
mkdir -p "$DEST"
cp "$SRC_DIR/server.py" "$SRC_DIR/index.html" "$SRC_DIR/kiosk.sh" "$DEST/"
chmod +x "$DEST/kiosk.sh"

echo "==> systemd servisi kuruluyor..."
cp "$SRC_DIR/netdash.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable netdash
# restart: servis zaten calisiyorsa yeni kod ancak boyle devreye girer
# (server.py index.html'i acilista bellege alir, kopyalamak yetmez)
systemctl restart netdash

if command -v ufw >/dev/null 2>&1 && ufw status | grep -q "Status: active"; then
  echo "==> ufw aktif; 8377/tcp aciliyor..."
  ufw allow 8377/tcp comment "netdash dashboard" >/dev/null
fi

echo "==> Kiosk otomatik baslatma ayarlaniyor..."
# sudo ile calistirildiginda gercek masaustu kullanicisini bul
KIOSK_USER="${SUDO_USER:-}"
if [ -n "$KIOSK_USER" ] && [ "$KIOSK_USER" != "root" ]; then
  AUTOSTART_DIR="$(getent passwd "$KIOSK_USER" | cut -d: -f6)/.config/autostart"
  mkdir -p "$AUTOSTART_DIR"
  cp "$SRC_DIR/netdash-kiosk.desktop" "$AUTOSTART_DIR/"
  chown -R "$KIOSK_USER:" "$AUTOSTART_DIR"
  echo "    -> $AUTOSTART_DIR/netdash-kiosk.desktop"
else
  echo "    !! SUDO_USER bulunamadi; netdash-kiosk.desktop dosyasini elle"
  echo "       ~/.config/autostart/ altina kopyalayin."
fi

echo "==> Ekranin kararmasini kapatmak icin (masaustu kullanicisi olarak):"
echo "    gsettings set org.gnome.desktop.session idle-delay 0"
echo "    gsettings set org.gnome.settings-daemon.plugins.power idle-dim false"
echo
echo "Kurulum tamam. Sunucu 0.0.0.0:8377'de dinliyor (kimlik dogrulama YOK)."
echo "Kiosk ekrani aciksa yeni arayuzu gormek icin sayfayi yenileyin veya cihazi"
echo "yeniden baslatin (tarayici eski sayfayi tutuyor olabilir)."
echo "Yerelde test: http://127.0.0.1:8377"
echo "Ag icinden: http://$(hostname -I | awk '{print $1}'):8377"
echo "Disaridan erisim icin router'da 8377 portunu bu cihaza yonlendirmeniz gerekir."
echo "Yeniden baslatinca pano tam ekran acilacak."
