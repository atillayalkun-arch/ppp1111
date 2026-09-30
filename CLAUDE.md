# YouTube faceless kanal projesi: durum notları

Bu dosya yeni bir oturumda bağlamı hızlıca geri yüklemek içindir. Kısa tut, güncel tut.

## Kullanıcı ve çalışma tarzı
- Türkçe konuş. Adım adım ilerle, önce soruyu yanıtla, toplu doküman/kod yazma.
- Kullanıcı her yanıtın sonunda kullanım bilgisi görmek istiyor: bağlam penceresi (kullanıcının gösterdiği değer) ve "Cloud session credits". Tahmini uydurma rakam verme.
- API anahtarı asla sohbete, dosyaya veya commit'e girmez (`YT_API_KEY` yalnızca kullanıcının terminalinde). Ekran görüntüsünde anahtar görürsen uyar ve yenilemesini söyle.
- Token verimliliği: gereksiz dosya okuma yok, büyük çıktıları yapıştırtma (özet iste), ucuz/ham işleri script veya başka AI'ya (Gemini) bırak, karar ve sentez burada yapılır.

## Proje amacı
Japonca, yüzsüz (faceless), AI destekli ama yüksek kalite (senaryo, motion grafik, özgün shot tasarımı) bir YouTube kanalı. Kullanıcının kanalı: ミラー心理学 (@mirashinrigaku, 1 video, mavi karakter). Ana niş adayı: Japonca insan davranışı ve psikoloji açıklamaları (talep kanıtlı ama dalga ve klonlaşma riski var).

## Verilen stratejik kararlar
- Niş = izleyici ve mercek, konu havuzu değil. 4 katman: izleyici, duygusal getiri, imza mercek, yenilenen girdi ("300. videonun konusu nereden gelecek?" testi).
- Kopyalama yok: benzerlik noktaları (parity) korunur, 1-2 farklılık noktası (difference) seçilir; ERRC ve konumlandırma haritası kullanılır.
- Farklılaşma adayları: mekanizma görselleştirme (motion), kaynak/kanıt katmanı, özgün anlatı yapısı. Konsept adayları: (A) gündelik olay x bilim merceği, (B) zihin/algı tuhaflıkları, (C) bir anın içinde zihin, (D) Japon toplumunun psikolojisi. Veriyle seçilecek.
- Konu bulma: talep kanıtı x yeni açı x kaynak avantajı; boşluk haritası makineyle çıkarılır, son zevk kararı kullanıcıda.
- Kullanıcının Japonca kalite hattı: konu araştırması, derin malzeme toplama, beat planı, paketleme (hook, kapak), voice-id ile yazım, ana dilli okuyucu filtresi. İlk 3-5 videoda ana dilli örnekleme yalnızca kalibrasyon için.
- İlk videolar 8+ dk. Rakipler çoğunlukla 18-23 dk ("dinleme" izleyicisi hipotezi, veriyle sınanacak).
- Survivorship bias: başarısız/durmuş kanallar da analiz edilir. Global kanallar ayrı referans grubu.

## Faz 0: 9 katman ve durum
| # | Katman | Durum |
|---|---|---|
| 1 | Kanal keşfi (39 kanal toplandı) | TAMAM |
| 2 | Kanal profili | TAMAM (collect.py + analyze.py) |
| 3 | Video listesi ve metrikler | TAMAM |
| ara | Eleme ve sınıflandırma: kota kontrolü, kanal başına ekran görüntüsü, Gemini ile nitel not, labels.txt (core/neighbor) | SIRADA |
| 4 | Örneklem seçimi (select_sample.py, nihai listeden) | bekliyor |
| 5 | Transkript, küçük resim, yorum toplama (seçilen videolar) | bekliyor |
| 6 | Temizlik ve kalite kontrol | bekliyor |
| 7 | Video başına yapısal analiz (Gemini, JSON şeması) | bekliyor |
| 8 | Yorum analizi (Gemini) | bekliyor |
| 9 | Sentez: parity/difference, konumlandırma, ERRC, boşluklar (burada, Claude) | bekliyor |
Sonra: Faz 1 konsept adayları, Faz 2 kanal DNA dokümanı (md, voice-id ile bağlantılı), Faz 3 pilot konu üretimi.

Kota planı: core-big 5, core-rising 7, core-stalled-or-weak 4, neighbor 14, global ~7.

## Dosyalar (`kanal-arastirma/`) ve çalıştırma (kullanıcının bilgisayarında)
- `collect.py`: API'den ham veri (data/raw/*.json). `analyze.py`: metrikler, kategoriler, kanal başına `out/channels/<bucket>/<kanal>/profile.md` + `videos.csv`, `channels_full.csv`, `videos_full.csv`, `group_report.txt`, `channel_briefs.json`. `select_sample.py`: nihai kanallardan örneklem. `labels.txt` (opsiyonel): `kanal adı | core/neighbor/global/own`.
- Kategoriler veriden çıkar: ja-big (100K+), ja-rising (ilk video <12 ay), ja-stalled-or-weak, ja-other, global (başlıklarda kana yoksa), own.
- Çalıştırma (PowerShell): `$env:YT_API_KEY="..."`, `$env:PYTHONUTF8="1"`, `python collect.py channels.txt`, `python analyze.py`.
- `data/`, `out/`, `channels.txt` git'te yok; kullanıcının bilgisayarında. Bu oturumdan görülemez; gerekirse kullanıcı `group_report.txt` veya `channel_briefs.json` yapıştırır.

## Durum
- Script'ler gerçek API'de çalıştı: 39 kanal toplandı, kategoriler oluştu.
- Sıradaki: `group_report.txt` içeriğini görüp kota/eksikleri belirle, kanal başına ekran görüntüsü planı, Gemini'ye verilecek eleme istemi, labels.txt.
- Açık iş: eski API anahtarı bir ekran görüntüsünde görüldü; yenilendiğini teyit et.
