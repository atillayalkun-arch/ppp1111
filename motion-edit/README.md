# Işık Kapanmadan Önce — Motion Edit

15 sn, 1920×1080, 30 fps. Katmanlı asetlerden kodla üretilmiş motion edit.

## Yapı

| Yol | İçerik |
|---|---|
| `source/` | Orijinal görsel ve teslim edilen asetler (değiştirilmez) |
| `tools/prep.py` | Ön hazırlık: temiz arka plan, eksik katmanların (yatak, lamba, düğme, etiketler) orijinalden kesilmesi, iz balonlarının ayrılması, doğrulama |
| `assets/` | Hazırlanmış katmanlar + `layers.json` (orijinal tuvaldeki konumlar) |
| `index.html` | Animasyon motoru: tarayıcıda açınca canlı oynar, tıklayınca baştan başlar |
| `render.mjs` | Kare kare render → `motion-edit.mp4` |

## Çalıştırma

```bash
pip install pillow numpy opencv-python-headless imageio-ffmpeg
python3 tools/prep.py                 # assets/ klasörünü yeniden üretir
node render.mjs                       # motion-edit.mp4
node render.mjs --frames 90,200,360   # sadece önizleme kareleri (preview/)
```

Canlı izlemek için klasörü bir yerel sunucuyla açın (ör. `npx serve .`) ve `index.html`'e gidin.

## Motorun ana fikirleri

- **2.5D kamera:** Her katmanın bir derinliği var (duvar 0.90, yatak 0.95, karakter 1.0, balonlar 1.07, toz 1.28). Kamera her katman için ayrı merkez ve ölçek hesaplar. Böylece paralaks ve dolly etkisi oluşur. Orijinal kompozisyon, kamera başlangıç konumundayken piksel piksel korunur.
- **En-boy oranı sabit:** Sadece eşit ölçek kullanılır. Dönüş sırasında bile en uzak katman kadrajı tamamen kaplar.
- **Kamera eğrileri:** Monoton kübik interpolasyon (aşma yok), zoom log uzayında.
- **Hareket bulanıklığı:** Her kare 10 alt kareden birleştirilir (180° obtüratör).
- **Alan derinliği:** Katman bazında. Bulanıklık seviyeleri önceden hesaplanır ve çizimde aralarında birebir geçiş yapılır.
