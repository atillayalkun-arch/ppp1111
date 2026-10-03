# Tasarım ve kompozisyon planı: "Açık sekme" videosu (Aşama 1-4)

Bu doküman edit planının girdisidir. Kimlik, sahne dünyaları, tetikleyici-görsel karşılıkları ve shot kompozisyonlarını içerir. Hareket ve zamanlama tarifi için `edit_plani.md` kullanılır, ikisi birlikte kodlayan modele verilir.

**Varsayımlar:** Stil için paylaşılan ikinci görsel ("ŞİMDİ." karesi) referans alındı. Süreler, anlatım hızı 2,7 kelime/saniye varsayılarak hesaplandı, gerçek ses kaydıyla kalibre edilecek. Tüm koordinatlar 1920×1080 üzerinde. Henüz render görülmedi, kompozisyon kararları tasarım niyetidir ve ekran görüntüleriyle doğrulanacak.

---

## AŞAMA 1: Kimlik

**Ana fikir (tek cümle):** Beyin, bitmemiş işi kapanmayan bir sekme gibi açık tutar. Yarına yazılan plan o sekmeyi kapatır.

**Görsel aile: "Açık sekme kartı".** Bitmemiş her şey (yarım mail, ödenmemiş sipariş, yarım iş) baş üstünde yüzen küçük bir sekme kartı olarak görünür. Karta bağlı olduğu kişiden ince kesikli bir bağ çizilir. Kart kapanınca sahneden gider. Böylece 9 shot'ın hepsi tek metaforla bağlanır: mail kartı (S2-S3) → sipariş kartları (S6) → tarayıcıdaki beyin (S7) → kapanan sekme (S9).

**Ton:** Sakin, samimi, hafif mizahlı. Tempo orta. Her shot tek odak.

**Stil adı:** "Sıcak kâğıt, kalın kontur" (referans görselden): krem zemin, kalın koyu kontur, düz renk, kâğıt grain'i, sınırlı sıcak palet, üstte iri kalın başlık yazısı, yere düşen ışık paralelkenarı.

### Tasarım token'ları

| Rol | Hex | Kullanım kuralı |
|---|---|---|
| zemin_duvar | #F2E8D5 | Duvar, köprü zemini |
| zemin_yer | #E4D3B6 | Zemin |
| kemik | #F7F1E3 | Kart, defter, tarayıcı içi |
| kontur | #2B1D16 | Tüm ana konturlar |
| vurgu (tek doygun) | #E8532F | Yalnızca "açık/bitmemiş" bilgi: sekme kartları, "NEDEN Mİ?" |
| tamam | #7A9A5B | Yalnızca "kapanmış/ödenmiş": S6 damga, S9 kapanış |
| hardal | #EDA93A | Güneş, ışık hüzmesi, kişinin bere detayı |
| kiremit | #8B3A22 | Büyük mobilya (koltuk benzeri yüzeyler) |
| gövde_koyu | #4A3A33 | Kişi kıyafeti, gölge |
| ten | #EBC4A0 | Yüz, el |
| somon | #F0B49A | Beyin |
| su | #B7D0D6 | Yalnızca su damlaları |
| gök_akşam | #E8C39A | Alacakaranlık gökyüzü |
| gök_derin | #C9906A | Gece öncesi gökyüzü |
| sepya_katman | #D9C3A0, %12 | Yalnızca 1920 Berlin sahnesi |

- **Çizgi:** ana kontur 6 px, detay 3 px, uçlar yuvarlak (`round`). Bağlantı çizgisi 3 px, kesikli (14/10).
- **Doku:** tüm kareye grain (feTurbulence, baseFrequency 0.8, opaklık 0.10). Nesnelerin zemine değdiği yere yumuşak temas gölgesi (elips, kontur rengi %12).
- **Tipografi:** başlık ve etiketler Anton (yedek: Bebas Neue, Impact). Büyük harf `toLocaleUpperCase('tr-TR')` ile (İ ve Ş doğru çıksın). Başlık 160-300 px, etiket 44-96 px. *Doğrulanacak: Türkçe karakter desteği.*
- **Hareket:** pop = easeOutBack (taşma 1.2), 0.45 sn · slide = easeOutCubic, 0.6 sn · move = easeInOutCubic · stagger = 0.12 sn · kamera easeInOutSine.
- **Kamera dili:** yalnızca yavaş itme (zoom-in, ölçek 1.00→~1.10), el titremesi yok.
- **Geçiş dili:** sahne değişimi = 0.5 sn yatay kayma, ortak zemin çizgisi y=860 kaymada sabit kalır. Köprü = sert kesme + 0.25 sn pop. Aynı sahne içi shot değişimi = eski ön plan 80 px sola kayıp 0.3 sn'de kaybolur, yenisi girer (arka plan kalır).
- **Kişi:** ayakta boy 300 px (kare yüksekliğinin %28'i), kafa 62 px, kapsül gövde, ince bacak. Yüz: nokta göz, kaş çizgisi, tek çizgi ağız. Duruş hafif omuz düşük.
- **Kompozisyon çerçevesi:** kenar boşluğu x 120–1800, y 90–990; zemin çizgisi y=860; merkez ekseni x=960; üçlü çizgiler x=640/1280.

---

## AŞAMA 2: Sahne dünyaları ve sabit varlıklar

| Sahne | Shot | Dünya | Işık / palet | Zemin çizgisi |
|---|---|---|---|---|
| A. Ev, günün sonu | 1-3 | Yatak odası (S1-2), duş ve yemek köşesi (S3, panel olarak) | Akşam, sıcak. Gün batarken gök_akşam→gök_derin. Işık soldan | y=860 |
| B. Köprü | 4 | Dünya yok, düz zemin_duvar | Işık yok | ince çizgi y=860 (çapa) |
| C. 1920'ler Berlin restoran | 5-6 | Restoran içi: yuvarlak masalar, sarkık lamba, dama zemin, lambri bandı | Aynı palet + sepya_katman, lamba ışığı | y=860 |
| D. Beyin ve sekme | 7 | Soyut: kemik zemin, %6 nokta ızgarası, ortada tarayıcı penceresi | Düz, ışık yok | pencere alt kenarı y=860 |
| E. Ev, çözüm | 8-9 | Sahne A'nın odası: masa, defter, lamba, A'daki pencere (gece öncesi gökyüzüyle) | Lamba ışığı + gök_derin | y=860 |

**Sabit varlıklar** (tek fonksiyon, tüm shot'larda yeniden kullanılır):

| Varlık | Parametreler | Kullanıldığı shot |
|---|---|---|
| `kişi()` | poz (yatan/ayakta/oturan), ifade (sakin/endişeli/rahat), x, y | 1,2,3,8,9 |
| `sekmeKartı()` | içerik (zarf/sipariş/iş), ilerleme 0-1, durum (açık/kapalı), x, y, ölçek | 2,3,6,7,8,9 |
| `beyin()` | parıltı 0-1, x, y, ölçek | 7,9 |
| `tarayıcıPenceresi()` | sekmeler[], x, y, genişlik | 7,9 |
| `garson()`, `psikolog()` | poz | 5,6 |

**Sekme kartı tasarımı:** kemik dikdörtgen, 6 px kontur, sol üstte sekme çıkıntısı, sağ üstte küçük ×, içinde ikon ve ilerleme çubuğu. Açıkken vurgu rengi (üst şerit + çubuk), kapalıyken tamam rengi.

---

## AŞAMA 3: Tetikleyici → görsel karşılık

Ölçüt: yazısız anlaşılır mı, aileye uyar mı. İlişki tetikleyicileri (Ama, ise, bile, gibi) görsel araçla taşınır.

| Shot | Tetikleyici | Görsel karşılık |
|---|---|---|
| 1 | akşam | Pencerede alçak güneş, gökyüzü sıcak, yere ışık hüzmesi |
| | yatak | Yatak (başlık, şilte, yastık) yandan |
| | uzanan kişi | `kişi()` yatağın kenarında oturur |
| | uzanma | Kişi yavaşça yatar |
| | günün bitişi | Güneş pencere altına batar, gökyüzü kararır |
| 2 | Ama | Sarsıntı (6 px, 0.2 sn) + sahne renkleri %15 solar: huzurun kırılması |
| | kafan | Kişinin gözü açılır, kaşlar endişeli; kafanın üstünde boş kart çerçevesi |
| | hâlâ | Işık kararırken kart olduğu yerde sallanır: zaman geçiyor, kart gitmiyor |
| | yarım kalan | Kartın içinde ilerleme çubuğu %60'a dolar ve takılır |
| | mail | Kartta zarf ikonu |
| | mailde (bağ) | Kafadan karta kesikli bağ çizgisi |
| 3 | duş alma | Sol panel: duş başlığı, su damlaları, kişi altında |
| | yemek yeme | Sağ panel: masa, tabak, kişi çatalla |
| | bile | İki karttan aynı kartın bağ çizgisiyle bağlanması: kart her yerde aynı |
| | aklına geliyor | Kartlarda çift halka dalgası, kaşlar kalkar |
| 4 | neden sorusu | Devasa "NEDEN Mİ?" başlığı, soru işareti son girer |
| 5 | 1920'ler, Berlin | Sol üst etiket: "1920'LER · BERLİN" |
| | psikolog | Gözlüklü, saçı topuz, elinde defter, masada oturan figür; altında "Bluma Zeigarnik" etiketi |
| | restoran | Masalar, sarkık lamba, dama zemin, lambri bandı |
| | garsonlar | İki garson, önlük ve kelebek papyon, tepsili |
| | izleme | Psikolog gözünden garsona kesikli bakış çizgisi, defterde kalem hareketi |
| 6 | garsonlar | Tek garson büyük (referans S5) |
| | siparişler | Garsonun üstünde 3 sipariş kartı (adisyon ikonlu) |
| | ödenmemiş | Kartlar vurgu renginde + kartta boş madeni para çizgisi |
| | hepsini | Üç kart eşzamanlı nabız atar |
| | aklında tutma | Kafadan her karta bağ çizgisi, garson başını sallar |
| | hesap kapanması | Ortada hesap kâğıdı, üstüne tamam rengi onay damgası |
| | ise (zıtlık) | Dikey kesikli ayırıcı, sağ sütunda aynı garson (aynı poz, aynı boy) |
| | unutma | Sol kartlar tamam rengine dönüp sağa uçar, sağda hayalet (kesikli) kart olur; garson omuz silker |
| 7 | beyin | `beyin()` ortada |
| | tamamlanmamış iş | Beynin üstünde 3 yarım kart (zarf, sipariş, görev) |
| | açık sekme | Kartlar tarayıcı sekme şeridine yerleşir, pencere çerçevesi çizilir |
| | gibi tutar (benzetme) | Beyin pencerenin içeriği olur, sekmelerle bağ çizgileri, hafif parıltı |
| | bitirmeden kapanmaz | İmleç × tuşuna tıklar, sekme esneyip geri sıçrar |
| 8 | çözüm vaadi | "ÇÖZÜM BASİT." başlığı |
| | yapamıyorsan bile | Kişi oturur, başının üstündeki kart soluk açık kalır (çubuk %60'ta takılı) |
| | yarın | Defterin başlığında "YARIN" |
| | plan | Defter sayfasında 3 satırlık plan şablonu |
| | yazma | Kalem satırları tek tek yazar |
| 9 | beyin | Kişinin üstünde düşünce balonu içinde mini tarayıcıdaki beyin |
| | sekme | Balonda tek açık sekme |
| | kapanma | İmleç × tıklar, sekme tamam rengine döner ve kapanır, parıltı söner, kişi gözünü kapar |

---

## AŞAMA 4: Shot planları (kompozisyon ve görsel gramer)

Bölge gösterimi: [x1–x2 × y1–y2]. t = shot başından saniye.

### S1 · "Akşam yatağa uzandın. Gün bitti." · 2.4 sn · Sahne A
- **Kompozisyon:** Pencere [200–620 × 150–470] sol üst. Yatak [700–1560 × 700–860], başlık sağda. Kişi yatakta gövde [1140–1440 × 690–760], baş yastıkta (1420, 715). Işık hüzmesi pencereden yatağa diyagonal. **Boş bölge [1250–1560 × 400–640]** S2'deki kart için ayrıldı.
- **Okuma sırası (Z):** pencere (akşam) → yatak → kişi → batan güneş.
- **Giriş zamanları:** t0.0 akşam (gökyüzü, güneş alçak) · t0.3 yatak (aşağıdan slide) · t0.6 kişi oturur · t0.9 uzanır (0.6 sn) · t1.6 güneş batar (0.7 sn).
- **Vurgu:** vurgu rengi yok (kasten): ilk kareler sakin, S2'deki kırılma güçlensin. Odak: kişi + yatak.
- **İlişki çizgisi:** ışık hüzmesi (pencere→yatak).
- **Kamera:** ölçek 1.00→1.05, merkez (960,540)→(1100,620).
- **Çapa:** zemin çizgisi y=860, yatak ayakları çizgide.

### S2 · "Ama kafan hâlâ o yarım kalan mailde." · 2.8 sn · Sahne A
- **Kompozisyon:** S1 arka planı aynen. Kart [1330–1520 × 440–580] (190×140), kafanın üstünde; bağ (1420,650)→(1420,580). Pencere solda.
- **Giriş zamanları:** t0.0 Ama (sarsıntı, renk %15 solar) · t0.4 kafan (göz açılır, boş kart çerçevesi pop) · t0.9 hâlâ (ışık kararır, kart sallanır) · t1.4 yarım kalan (çubuk %60'a dolar, takılır ×2) · t1.9 mail (zarf pop) · t2.3 bağ çizgisi (0.4 sn).
- **Vurgu:** kart tek doygun vurgu; boyutu %115 büyütülür. Bağlam (pencere, yatak) solgun.
- **Kamera:** 1.05→1.12, merkez kartın yönüne (1250,560).
- **Geçiş (S3'e):** ön plan 80 px sola kayıp kaybolur.
- **Çapa:** aynı yatak, aynı kafa-kart ilişkisi S3'e taşınır (kart boyutu ve bağ stili).

### S3 · "Duş alırken, yemek yerken bile aklına geliyor." · 2.8 sn · Sahne A
- **Kompozisyon:** İki eşit panel (yuvarlak köşeli, 6 px kontur): sol [120–900 × 150–860], sağ [1020–1800 × 150–860]; panel içi zemin y=860 ortak. Sol: duş başlığı [440–600 × 200–260], kişi ayakta x=510. Sağ: masa [1180–1640 × 640–860], kişi oturan x=1410. İki kart aynı boy ve aynı y: sol [415–605 × 380–520], sağ [1315–1505 × 380–520].
- **Giriş zamanları:** t0.0 duş (sol panel, su başlar; kart t0.3) · t0.8 yemek (sağ panel, kart t1.1) · t1.5 bile (iki kart arası yatay kesikli bağ çizilir, kartlar aynı anda parlar) · t2.0 aklına geliyor (kartlarda çift halka dalgası, kaşlar kalkar).
- **Vurgu:** iki kart (aynı, vurgu rengi). Paneller sakin.
- **Kamera:** 1.00→1.03, sabit merkez.
- **Geçiş (köprüye):** sert kesme.

### S4 · "Neden mi?" · 1.0 sn · Köprü
- **Kompozisyon:** tam kare zemin_duvar. "NEDEN Mİ?" Anton ~300 px, vurgu rengi, [300–1620 × 330–630], taban çizgisi y=630. İnce zemin çizgisi y=860 soldan sağa çizilir (çapa).
- **Giriş:** t0.0–0.5 harfler 0.06 sn arayla pop; "?" en son, taşmalı.
- **Vurgu:** tüm kare başlık. **Kamera:** 1.00→1.03.
- **Geçiş (S5'e):** 0.5 sn yatay kayma, zemin çizgisi sabit.

### S5 · "1920'lerde Berlin'de bir psikolog, Bluma Zeigarnik, bir restoranda garsonları izledi." · 3.6 sn · Sahne C
- **Kompozisyon:** Etiket "1920'LER · BERLİN" [120–740 × 90–190]. Psikolog sol: masa [160–520 × 650–860], oturan figür x≈260, defter [300–420 × 650–670], isim etiketi [160–520 × 890–940]. Restoran orta: iki yuvarlak masa [700–1100 × 700–860], sarkık lamba x=960 (y 0–300), lambri bandı y 700–860, dama zemin y 860–1080. Garsonlar sağ: x≈1380 ve 1620 (tepsili).
- **Okuma sırası:** etiket → psikolog → restoran → garsonlar → bakış çizgisi.
- **Giriş zamanları:** t0.0 "1920'LER" · t0.4 "BERLİN" · t0.8 psikolog + isim t0.9 · t1.5 restoran (masalar, lamba, zemin slide) · t2.2 garsonlar (stagger) · t2.9 bakış çizgisi (psikolog gözü (300,640) → garson göğsü (1380,700)) + kalem hareketi.
- **Vurgu:** psikolog ve garsonlar (en büyük, en yüksek kontrast); vurgu rengi yok. Bağlam (lamba, masalar) solgun.
- **Kamera:** 1.00→1.05, merkez (960,540)→(1200,560).
- **Çapa:** zemin çizgisi y=860, S6'ya garsonlar ve arka plan aynen.

### S6 · "Garsonlar ödenmemiş siparişlerin hepsini aklında tutuyordu. Hesap kapanır kapanmaz ise hepsini unutuyordu." · 4.6 sn · Sahne C
- **Kompozisyon:** İki eşit sütun (aynı garson, aynı poz, aynı boy, eşit aralık): sol [120–900 × 150–860], sağ [1020–1800 × 150–860], garsonlar x=510 ve x=1410. Sol: 3 kart (150×110, 30 px aralık) [255–765 × 400–510], bağ çizgileri kafa (510,560)'tan. Sağ: aynı yerde 3 **hayalet (kesikli)** kart [1155–1665 × 400–510]. Orta: dikey kesikli ayırıcı x=960 (y 200–860), hesap kâğıdı [880–1040 × 560–720].
- **Giriş zamanları:** t0.0 garson sol · t0.4 3 sipariş kartı (stagger) · t1.0 ödenmemiş (kartlar vurgu, boş para çizgisi) · t1.5 hepsini (3 kart eşzamanlı nabız) · t1.9 aklında tutuyordu (bağ çizgileri, baş sallama) · t2.5 hesap (kâğıt slide) + damga t2.8 (tamam rengi, 8 px sarsıntı) · t3.0 ise (ayırıcı çizilir, sağ sütun slide) · t3.3 unutuyordu (sol kartlar tamam rengine dönüp hayalet olur, sağ garson omuz silker).
- **Vurgu:** kartlar (sol sütun) en yüksek kontrast; damga tamam rengi (tek seferde tek doygun renk kuralı: kartlar solarken damga girer).
- **İlişki çizgileri:** bağ çizgileri, dikey ayırıcı. **Kamera:** 1.00→1.04 sabit merkez.
- **Çapa:** zemin çizgisi y=860, aynı restoran zemini.
- **Geçiş (S7'ye):** 0.5 sn yatay kayma, zemin çizgisi sabit.

### S7 · "Beynin tamamlanmamış işi açık sekme gibi tutar. Bitirmeden kapanmaz." · 3.4 sn · Sahne D
- **Kompozisyon:** Tarayıcı penceresi [360–1560 × 170–860], üst şerit y 170–260. Sekmeler [400–620], [640–860], [880–1100] × [190–260] (zarf, sipariş, görev). Beyin [760–1160 × 380–780], merkez (960,580). İmleç başlangıç (1300,700).
- **Giriş zamanları:** t0.0 beyin · t0.6 üç yarım kart beynin üstünde ([700–1220 × 300–350]) · t1.3 açık sekme (kartlar şeride yerleşir, pencere çerçevesi çizilir) · t1.9 gibi tutar (beyinden sekmelere kesikli bağ, parıltı) · t2.4 bitirmeden kapanmaz (imleç ×'e tıklar, sekme esneyip geri sıçrar).
- **Vurgu:** beyin + açık sekmeler; vurgu rengi yalnızca sekmelerde. **Kamera:** 1.00→1.06, beyne.
- **Çapa:** pencere alt kenarı y=860 zemin çizgisi hizasında.
- **Geçiş (S8'e):** 0.5 sn yatay kayma.

### S8 · "Çözüm basit: yapamıyorsan bile, yarına bir plan yaz." · 3.2 sn · Sahne E
- **Kompozisyon:** Başlık "ÇÖZÜM BASİT." [420–1500 × 100–260] (kontur rengi, vurgu değil). Kişi taburede x≈780. Kart [685–875 × 360–500], %70 opaklık. Masa [900–1500 × 640–860]. Defter [1000–1360 × 560–650]. Lamba [1560–1640 × 380–640] ve lambadan deftere ışık paralelkenarı. Pencere sol üst (S1'deki, gece öncesi).
- **Okuma sırası:** başlık → kart → defter → lamba.
- **Giriş zamanları:** t0.0 başlık (harf stagger) · t0.6 kişi oturur, kart soluk, çubuk %60'ta takılı · t1.3 "YARIN" defter başlığı · t1.7 3 satırlık plan şablonu · t2.0 kalem satırları yazar (satır başına 0.3 sn).
- **Vurgu:** defter (en büyük, ışıkla en yüksek kontrast). Kart kasten solgun.
- **Kamera:** 1.00→1.05, deftere (1180,640).
- **Geçiş (S9'a):** aynı sahne, ön plan kayıp çıkar.

### S9 · "Beynin sekmeyi kapatır." · 1.8 sn · Sahne E
- **Kompozisyon:** Aynı oda, defter dolu. Düşünce balonu [640–1160 × 120–520], kuyruk kişinin başına (780,560). Balonda mini tarayıcı [700–1100 × 170–440], beyin [830–970 × 270–410], tek sekme [720–840 × 180–220].
- **Giriş zamanları:** t0.0 beyin (balon pop) · t0.4 sekme · t0.9 kapanır (imleç ×, sekme tamam rengine döner, kapanır, parıltı söner) · t1.4 kişi gözünü kapar, gülümser.
- **Vurgu:** balon içi (tek açık sekme vurgu rengi, kapanınca tamam rengi). **Kamera:** 1.00→1.08, balona (900,380).
- **Bitiş:** t1.8'de sakin tutuş (kamera dururken 0.3 sn).

---

## Süre özeti ve süreklilik

| Shot | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | Toplam |
|---|---|---|---|---|---|---|---|---|---|---|
| sn | 2.4 | 2.8 | 2.8 | 1.0 | 3.6 | 4.6 | 3.4 | 3.2 | 1.8 | **25.6** |

| Geçiş | Ortak çapa |
|---|---|
| S1→S2→S3 | Aynı arka plan (S1-2), zemin çizgisi y=860, aynı kart tasarımı ve kafa-kart bağı |
| S3→S4 | Sert kesme; köprüde zemin çizgisi çizilir |
| S4→S5→S6 | Zemin çizgisi y=860 kayma boyunca sabit; S5-6 aynı restoran ve aynı garsonlar |
| S6→S7 | Zemin çizgisi, pencere alt kenarı y=860 |
| S7→S8 | Zemin çizgisi y=860, aynı sekme kartı |
| S8→S9 | Aynı oda, aynı kişi konumu |

## Kodlayıcıya kurallar
- Tek proje, 1920×1080 SVG, zaman çizelgeli ve ileri-geri sarılabilir.
- Her shot bir fonksiyon, token dosyası ve sabit varlık fonksiyonları ortak.
- Kamera ayrı katman. Shot'lar arası nesne taşıma yok.
- Bir shot'ta en çok 4±1 okunabilir grup.
- Vurgu rengi yalnızca "açık/bitmemiş" bilgide, tamam rengi yalnızca "kapanmış" bilgide.
- Etiket metinleri senaryodan alınır: "1920'LER · BERLİN", "Bluma Zeigarnik", "NEDEN Mİ?", "ÇÖZÜM BASİT.", "YARIN".
- Gözden geçirme ekran görüntüsüne dayanır, tahminle yargı yapılmaz.

## Doğrulanmamış / dikkat
1. Anton'un Türkçe karakter desteği.
2. Süreler ses kaydıyla kalibre edilecek.
3. S6 ve S7 yoğun, 4±1 eşiğinin üstüne çıkarsa ilk kırpılacak elemanlar: S6'da hayalet kartlar, S7'de bağ çizgileri.
4. S1-S9 kompozisyon koordinatları render görülmeden yazıldı, ilk turda düzeltme beklenmeli.
