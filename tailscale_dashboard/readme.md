# NetDash — Endüstriyel PC Ağ Paneli

Ubuntu üzerinde, açılışta tam ekran (kiosk) çalışan, koyu temalı ağ gösterge paneli.
10" dokunmatik ekran (1024×768) için tasarlandı; iki kart alt alta yerleşir.

## Gösterdikleri

| Veri | Kaynak | Yenilenme |
|---|---|---|
| Hostname + LAN IP | sistem | anlık (bellekten) |
| İnternet (public) IP | api.ipify.org vb. | **günde 1 kez**, sadece RAM'de tutulur |
| Aktif ethernet arayüzü (enp0s31f6 / enp1s0) anlık hız | `/proc/net/dev` | 1,5 sn |
| Ethernet saatlik / günlük / aylık toplam | vnstat | 60 sn (ekran), 5 dk (disk) |
| tailscale0 anlık hız | `/proc/net/dev` | 1,5 sn |
| tailscale0 saatlik / günlük / aylık toplam | vnstat | 60 sn (ekran), 5 dk (disk) |

Aktif ethernet arayüzü default route'a bakılarak otomatik seçilir; kablo diğer
porta takılırsa panel kendiliğinden ona geçer.

## SSD'yi koruyan tasarım kararları

- Anlık hızlar tamamen RAM'den okunur (`/proc/net/dev`) — hiç disk IO yok.
- Uzun dönem sayaçları tek disk yazarı olan **vnstat**'ta; `SaveInterval 5`
  ile diske 5 dakikada bir, birkaç KB yazar (günde ~1 MB'ın altında).
  Elektrik kesilirse en fazla son 5 dakikanın verisi kaybolur.
- Public IP diske hiç yazılmaz, bellekte tutulur.
- HTTP sunucusunun access log'u kapalı; systemd servisi stdout'u `null`'a basar.
- Kiosk tarayıcısı incognito modda; hem cache'i (`--disk-cache-dir`) hem profili
  (`--user-data-dir`) `/dev/shm`'de (RAM) tutar — GPU cache ve crash dump'ları
  dahil hiçbir tarayıcı verisi SSD'ye yazılmaz, her açılışta temiz başlar.

Kalan küçük hususlar (pratikte ihmal edilebilir):
- `netdash.service` yalnızca stderr'i journald'a yazar; normal çalışmada bu
  neredeyse boştur ve journald zaten kendi boyut sınırıyla döner (sınırsız büyümez).
- RAM kullanımı: tarayıcı cache + profil `/dev/shm`'de birkaç on MB tutar; 7/24
  çalışan uzun oturumlarda yavaşça artabilir, reboot'ta sıfırlanır. Endüstriyel
  PC'de sorun değil, ama RAM çok kısıtlıysa ara sıra yeniden başlatma yeter.

## Başka bir PC'ye kurmadan önce (kontrol listesi)

Betik çoğu şeyi otomatik yapar ama şu dört madde **her cihaza özeldir**:

1. **Ethernet arayüz adlarını güncelle.** `ip -br link` ile gerçek isimleri gör,
   sonra hem `server.py` (`LAN_IFACES`) hem `install.sh` (döngüdeki isimler)
   içindeki `enp0s31f6 enp1s0` değerlerini kendi kartlarınla değiştir. Yapılmazsa
   LAN hız/toplamları boş kalır. (`tailscale0` genelde sabittir.)
2. **Tarayıcı kurulu olsun:** `sudo apt install -y chromium-browser`
3. **Otomatik girişi aç:** Settings → Users → Automatic Login (betik yapmaz).
4. **Betiği masaüstü kullanıcısı olarak sudo ile çalıştır** (root shell'den değil),
   yoksa autostart yanlış kullanıcının evine gider:
   `sudo bash install.sh`

## Kurulum (Ubuntu cihazda)

Yukarıdaki dört maddeyi hallettikten sonra, bu klasörü cihaza kopyalayıp
masaüstü kullanıcısının terminalinde:

```bash
sudo bash install.sh
```

Betik şunları yapar: vnstat + curl kurar, `SaveInterval`'ı 5 dk yapar,
arayüzleri vnstat'a ekler, dosyaları `/opt/netdash`'a kopyalar,
`netdash.service`'i etkinleştirir ve masaüstü oturumu için kiosk otomatik
başlatmayı (`~/.config/autostart/`) kurar.

Sonra ekranın kararmaması için (masaüstü kullanıcısı olarak, sudo'suz):

```bash
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.settings-daemon.plugins.power idle-dim false
```

Yeniden başlatın; panel tam ekran açılır.

## Dışarıdan erişim

Sunucu `0.0.0.0:8377`'de dinler, yani makinenin **her ağ arayüzünden** erişilebilir
— **kimlik doğrulama yoktur**, IP:port'u bilen/tahmin eden herkes ağ istatistiklerini
görebilir (kontrol yapılamaz, sadece okunur veri).

- Yerel ağdan: `http://<cihazin-lan-ip>:8377` (kurulum betiği bu adresi ekrana yazar)
- Tailscale üzerinden: `http://<cihazin-tailscale-ip>:8377`
- İnternetten: router'da **8377/tcp** portunu bu cihazın LAN IP'sine yönlendirmeniz
  gerekir (port forwarding). ufw aktifse kurulum betiği yerel güvenlik duvarında
  8377'yi otomatik açar; router seviyesindeki yönlendirmeyi elle yapmanız gerekir.

## Sorun giderme: toplamlar güncellenmiyor

Panel, toplamları vnstat veritabanından okur; sorun neredeyse her zaman vnstat
tarafındadır. Sırayla kontrol edin:

1. **Panelin alt köşesindeki "son kayıt" saatine bakın.** Bu saat 5 dakikada bir
   ilerliyorsa vnstat sağlıklı demektir. Donmuşsa daemon veriyi yazamıyordur.
2. **Panelin ne gördüğünü bakın:** `curl -s http://127.0.0.1:8377/api/vnstat`
   — `"error"` varsa mesajı okuyun; değerler 0 ise vnstat henüz veri biriktirmemiştir.
3. **Daemon çalışıyor mu:** `systemctl status vnstat` ve
   `sudo journalctl -u vnstat -n 20 --no-pager`
4. **Veritabanı sahipliği bozuk mu:** `ls -la /var/lib/vnstat` — dosyalar `root`
   görünüyorsa daemon yazamıyordur. Düzeltme:
   `sudo chown -R vnstat:vnstat /var/lib/vnstat && sudo systemctl restart vnstat`
5. **vnstat sürümü:** `vnstat --version` — sunucu hem 1.x hem 2.x JSON şemasını
   destekler, ancak 2.x önerilir.

Taze kurulumda ilk değerler ancak ilk disk kaydından sonra (≤5 dk) görünür.

## Notlar

- Saatlik/günlük/aylık toplamlar vnstat'ın disk kaydını gösterir; en fazla
  5 dk gecikmeli olabilir (altta "son kayıt" saati yazar). Daha da canlı isterseniz
  `/etc/vnstat.conf` içinde `SaveInterval`'ı düşürün (yine de çok küçük bir yazma yükü).
- vnstat kurulumdan itibaren sayar; geçmişe dönük veri gösteremez.
- Arayüz adları değişirse `server.py` başındaki `LAN_IFACES` / `TS_IFACE`
  listesini güncelleyip `sudo systemctl restart netdash` deyin.
- Kiosk'tan çıkmak için klavye ile `Alt+F4` (veya `Ctrl+Alt+F3` ile konsola geçin).

## Dosyalar

- `server.py` — tek dosyalık Python sunucu (stdlib, bağımlılık yok), 0.0.0.0:8377
- `index.html` — koyu temalı panel arayüzü
- `netdash.service` — systemd servisi (DynamicUser, sıkılaştırılmış)
- `kiosk.sh` — Chromium/Firefox'u kiosk modda açan başlatıcı
- `netdash-kiosk.desktop` — masaüstü oturumunda otomatik başlatma girdisi
- `install.sh` — kurulum betiği
