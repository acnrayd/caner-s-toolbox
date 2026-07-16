#!/bin/bash
# NetDash kiosk baslatici — masaustu oturumu acilinca calisir.
# Tarayici cache'i RAM'de (/dev/shm) tutulur, incognito ile disk yazmasi minimal.
URL="http://127.0.0.1:8377"

# sunucu ayaga kalkana kadar bekle
for i in $(seq 1 60); do
  curl -fsS --max-time 2 "$URL/api/live" >/dev/null 2>&1 && break
  sleep 1
done

# Hem cache hem profil RAM'de (/dev/shm) -> SSD'ye yazma yok, her acilista temiz.
CACHE_DIR="/dev/shm/netdash-cache"
PROFILE_DIR="/dev/shm/netdash-profile"
mkdir -p "$CACHE_DIR" "$PROFILE_DIR"

for BIN in chromium-browser chromium google-chrome; do
  if command -v "$BIN" >/dev/null 2>&1; then
    exec "$BIN" --kiosk --incognito --noerrdialogs \
      --disable-session-crashed-bubble --disable-infobars \
      --user-data-dir="$PROFILE_DIR" \
      --disk-cache-dir="$CACHE_DIR" --disk-cache-size=1048576 \
      --app="$URL"
  fi
done

if command -v firefox >/dev/null 2>&1; then
  exec firefox --kiosk --private-window "$URL"
fi

echo "NetDash: uygun tarayici bulunamadi (chromium/firefox kurun)" >&2
exit 1
