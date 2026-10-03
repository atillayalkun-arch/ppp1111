# Edit planı: "Açık sekme" videosu (25.6 sn, 9 shot)

Bu plan, Aşama 1-4 girdisinin (token'lar, sahne dünyaları, tetikleyici-görsel tablosu, kompozisyon) üzerine **hareket yönetmenliğini** ekler. Koordinatlar ve bölgeler burada tekrar yazılmaz, Aşama 4'e referans verilir. Kod, fonksiyon adı ve çizim detayı yoktur. Kodlayan modele Aşama 1, 2, 4 ve bu plan birlikte verilir.

## Okuma kuralları

1. **Senkron:** Bir elemanın giriş hareketi, ilgili kelimenin söylendiği anda (tablodaki `t`) başlar. Ses kaydı gelince `t` değerleri kalibre edilir.
2. **Öncül hareket:** İmleç gibi eylem hazırlığı olan hareketler, tetikleyiciden en çok 0.3 sn önce başlayabilir. Eylemin kendisi `t`'de gerçekleşir.
3. **Geçiş süresi:** Sahne kayması (SAHNE_KAYMA), bitirdiği shot'un **son 0.5 sn'sine dahildir**. Yeni shot'un `t0.0`'ı kayma bittiğinde başlar. Bu yüzden toplam süre değişmez.
4. **Yeni nesne yok:** Aşama 4'te olmayan nesne eklenmez. Nesneye bağlı olmayan akıcılık hareketleri (nefes, sallanma, su akışı) "ikincil hareket" olarak ayrıca listelenir.
5. **Süre ve ease değerleri** yalnızca aşağıdaki sözlükten alınır. Tabloda başka değer varsa o satır istisnadır ve belirtilmiştir.

## Hareket sözlüğü

| Ad | Tarif | Süre / easing |
|---|---|---|
| **POP** | Ölçek 0.6→1.0, hafif taşma. İlk 0.15 sn'de saydamlık 0→1 | 0.45 sn, easeOutBack (taşma 1.2) |
| **SLIDE_IN(yön, mesafe)** | Belirtilen yönden ofsetle gelir, ilk 0.3 sn'de saydamlık 0→1. Varsayılan mesafe 100 px | 0.6 sn, easeOutCubic |
| **SLIDE_OUT** | 80 px sola kayar ve kaybolur | 0.3 sn, easeInOutCubic |
| **BELİR** | Ölçek 0.95→1.0 + saydamlık 0→1. Arka plan ve bağlam elemanları için | 0.3-0.4 sn, easeOutCubic |
| **ÇİZ** | Çizgi veya kontur başından sonuna doğru çizilir | Belirtilen süre, easeInOutCubic |
| **YAZ** | Kalem satırı soldan sağa çizer, kalem ucu çizgiyi takip eder | 0.3 sn/satır, easeInOutCubic |
| **MOVE** | Konumdan konuma | Belirtilen süre, easeInOutCubic |
| **NABIZ** | Ölçek 1→1.12→1 | 0.3 sn, easeInOutCubic |
| **SARSINTI(px)** | Yatay salınım, 3 salınım, genlik azalarak | 0.2 sn |
| **SALLAN** (döngü) | Dikey ±6 px, dönme ±1.5°, sinüs | Periyot 1.6 sn |
| **HALKA** | Kontur halkası ölçek 1→1.8, saydamlık 0.6→0. İki halka 0.15 sn arayla | 0.5 sn her biri, easeOutCubic |
| **TAKILMA** | Çubuk hedefe dolar, 5 puan geri döner, tekrar hedefe ulaşır; 2 tekrar | Toplam 0.4 sn |
| **ESNE-SIÇRA** | Sekme dar kesitte 0.7'ye sıkışır, 1.08'e taşar, 1.0'a oturur | 0.4 sn, easeOutBack |
| **NEFES** (döngü) | Ölçek ±1.5% | Periyot 3 sn |
| **STAGGER** | Arka arkaya girişler arası fark | 0.12 sn (harf girişlerinde 0.06 sn) |
| **KAMERA_İTME** | Ölçek ve merkez, shot boyunca doğrusal ilerler | Shot süresi, easeInOutSine |
| **SAHNE_KAYMA** | Eski sahne sola, yeni sahne sağdan kayar. Zemin çizgisi y=860 sabit | 0.5 sn, easeInOutCubic |
| **KÖPRÜ_KESME** | Sert kesme + ölçek 0.9→1.0 | 0.25 sn, easeOutBack |
| **İÇERİK_DEĞİŞİMİ** | Ön plan SLIDE_OUT, yenisi SLIDE_IN. Arka plan kalır | 0.3 sn çıkış + giriş |
| **IŞIK_DEĞİŞİMİ** | Gökyüzü ve ışık renk rolleri arasında geçiş | Belirtilen süre, easeInOutSine |

## Karakter oyunu kuralları

- **İfade değişimi** tetikleyiciden 0.1 sn sonra başlar (önce olay, sonra tepki). Süresi 0.15-0.2 sn.
- **Kişi (genel):** NEFES her zaman açık. Gözler nokta, kapalıyken kısa yay. Endişeli kaş: iç uçlar yukarıda (yaklaşık 12°). Rahat: kaşlar düz, gözler kapalı yay, hafif gülümseme. Hareketler küçük ve sakin, abartılı squash/stretch yok.
- **Yatma (S1):** Gövde oturandan yatana 0.6 sn'de döner, baş en son (0.1 sn gecikmeyle) yastığa iner, yastık hafif çöker (dikey ölçek 0.95, 0.2 sn).
- **Garson:** Baş sallama = iki kez ±6° dönme, toplam 0.4 sn. Omuz silkme = omuzlar 12 px yukarı 0.2 sn, 0.4 sn tutuş, geri iner.
- **Psikolog:** Defterde kalem döngüsü (0.8 sn). Baş garsonlara 5° döner (0.3 sn).
- **Tüm figürler:** Tek yönetmen kuralı: karakterin tepkisi, kartın (ya da olayın) tepkisinden sonra gelir.

## Shot başlangıç zamanları

| Shot | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | Bitiş |
|---|---|---|---|---|---|---|---|---|---|---|
| Başlangıç (sn) | 0.0 | 2.4 | 5.2 | 8.0 | 9.0 | 12.6 | 17.2 | 20.6 | 23.8 | 25.6 |

---

## S1 · Ev, akşam · 2.4 sn

**Amaç:** Huzurlu, sakin kurulum. Vurgu rengi yok, S2'deki kırılma güçlensin.

| t | Tetikleyici | Eleman | Hareket |
|---|---|---|---|
| 0.0 | akşam | Pencere, gökyüzü, güneş, ışık hüzmesi | Pencere ve gökyüzü BELİR (0.4 sn). Güneş pencerede alçakta durur. Işık hüzmesi pencereden yatağa doğru 0.5 sn'de uzar (maske silmesi, easeOutCubic) |
| 0.3 | yatak | Yatak | SLIDE_IN aşağıdan 100 px. Temas gölgesi 0.3 sn'de belirir |
| 0.6 | uzanan kişi | Kişi (oturan) | POP, ifade sakin. NEFES başlar |
| 0.9 | uzanma | Kişi, yastık | Oturandan yatana 0.6 sn (karakter kuralı: yatma) |
| 1.6 | günün bitişi | Güneş, gökyüzü, ışık hüzmesi | Güneş 0.7 sn'de pencere altına iner (easeInOutCubic). Aynı sürede gök_akşam→gök_derin (IŞIK_DEĞİŞİMİ). Işık hüzmesi %100→%60 ve daralır |

- **İkincil hareketler:** Kişi NEFES.
- **Kamera:** KAMERA_İTME 1.00→1.05, merkez (960,540)→(1100,620).
- **Geçiş:** S2'ye kesintisiz devam (aynı sahne, aynı arka plan, kamera sürer).
- **Süreklilik:** Pencere, yatak, kişi S2'de aynen. Boş bölge S2'deki kart için açık.
- **Kontrol kareleri:** t0.5, t1.5, t2.3.

## S2 · "Ama" kırılması · 2.8 sn

**Amaç:** Huzurun kırılması. Kart tek doygun vurgu olarak ilk kez girer.

| t | Tetikleyici | Eleman | Hareket |
|---|---|---|---|
| 0.0 | Ama | Tüm sahne | SARSINTI(6 px). Eş zamanlı sahne doygunluğu %100→%85 (0.3 sn, easeOutCubic), kalıcı |
| 0.4 | kafan | Kişi yüzü, kart çerçevesi | İfade sakin→endişeli (göz yaydan noktaya 0.15 sn, kaşlar 0.2 sn). Kafanın üstünde boş kart çerçevesi POP (vurgu rengi kontur) |
| 0.9 | hâlâ | Işık, kart | IŞIK_DEĞİŞİMİ gök_akşam→gök_derin 0.8 sn, ışık hüzmesi daralıp söner. Kart SALLAN başlar |
| 1.4 | yarım kalan | Kart çubuğu | Çubuk 0→%60 dolar (0.5 sn, easeOutCubic), ardından TAKILMA ×2 |
| 1.9 | mail | Kart ikonu | Zarf POP (kapağı yarı açık) |
| 2.3 | mailde | Kafa-kart bağı | Kesikli bağ kafadan karta ÇİZ, 0.4 sn |

- **İkincil hareketler:** Kart SALLAN (sürekli). Kişi NEFES (periyot 2.4 sn, stresli).
- **Kamera:** KAMERA_İTME 1.05→1.12, merkez kartın yönüne (1250,560).
- **Geçiş (S3'e):** İÇERİK_DEĞİŞİMİ. Ön plan (kişi, kart, yatak) SLIDE_OUT. Kamera aynı 0.3 sn'de 1.12→1.00'a döner.
- **Süreklilik:** Kart boyutu, bağ çizgisi stili ve kart/kafa ilişkisi S3'e taşınır.
- **Kontrol kareleri:** t0.2, t1.2, t2.7.

## S3 · Her yerde aynı kart · 2.8 sn

**Amaç:** "Aynı kart her yerde" fikrini, iki ortamda aynı kartla göstermek.

| t | Tetikleyici | Eleman | Hareket |
|---|---|---|---|
| 0.0 | duş alırken | Sol panel, duş başlığı, kişi | Sol panel SLIDE_IN soldan 120 px. Duş başlığı POP (t0.1). Kişi ayakta POP (t0.2). Su damlaları döngüsü başlar |
| 0.3 | (aynı tetikleyici) | Sol kart | Kart POP, bağ ÇİZ 0.25 sn |
| 0.8 | yemek yerken | Sağ panel, masa, tabak, kişi | Sağ panel SLIDE_IN sağdan 120 px. Masa, tabak, kişi POP stagger. Çatal döngüsü başlar |
| 1.1 | (aynı tetikleyici) | Sağ kart | Kart POP, bağ ÇİZ 0.25 sn |
| 1.5 | bile | İki kart arası bağ | Yatay kesikli bağ sol karttan sağa ÇİZ 0.5 sn. Bitince iki kart eş zamanlı NABIZ |
| 2.0 | aklına geliyor | Kartlar, kişiler | İki kartta eş zamanlı HALKA. İki kişinin kaşları 0.15 sn'de yukarı |

- **İkincil hareketler:** İki kart SALLAN, **aynı fazda** (aynı kart hissi). Su ve çatal döngüleri. Kişi NEFES.
- **Kamera:** KAMERA_İTME 1.00→1.03, sabit merkez.
- **Geçiş (S4'e):** Sert kesme.
- **Kontrol kareleri:** t0.7, t1.4, t2.5.

## S4 · Köprü: "NEDEN Mİ?" · 1.0 sn

**Amaç:** Hızlı, tipografik soru. Tüm kare başlık.

| t | Tetikleyici | Eleman | Hareket |
|---|---|---|---|
| 0.0 | neden sorusu | Başlık harfleri, zemin çizgisi | KÖPRÜ_KESME ile başlar. Harfler N-E-D-E-N-M-İ sırayla POP, aralık 0.06 sn (STAGGER istisnası). "?" en son, taşma 1.4, ardından ±8° sallanma 0.3 sn. Eş zamanlı ince zemin çizgisi y=860 soldan sağa ÇİZ 0.4 sn |

- **Kamera:** KAMERA_İTME 1.00→1.03.
- **Geçiş (S5'e):** SAHNE_KAYMA, t0.5-1.0 aralığında. Zemin çizgisi kayma boyunca sabit.
- **Kontrol kareleri:** t0.4, t0.9.

## S5 · 1920'ler Berlin restoran · 3.6 sn

**Amaç:** Yeni dünyayı kurmak: kim, nerede, neye bakıyor.

| t | Tetikleyici | Eleman | Hareket |
|---|---|---|---|
| 0.0 | 1920'lerde | Etiket "1920'LER" | POP. Arka plana sepya katmanı 0.5 sn'de %0→%12 |
| 0.4 | Berlin'de | Etiket "· BERLİN" | Aynı satıra POP |
| 0.8 | bir psikolog, Bluma Zeigarnik | Psikolog, masa, defter | SLIDE_IN soldan 100 px. t0.9'da isim etiketi BELİR (0.3 sn) |
| 1.5 | bir restoranda | Zemin, masalar, lambri, sarkık lamba | Dama zemin ve lambri sağdan SLIDE_IN. Masalar POP (STAGGER). Lamba yukarıdan SLIDE_IN 100 px, ardından bir kez sönümlü sallanma (±3°, 0.8 sn) |
| 2.2 | garsonları | İki garson | SLIDE_IN sağdan 120 px, STAGGER. Yürürken ±4 px dikey sekme, durunca tepsi hafif sallanır |
| 2.9 | izledi | Bakış çizgisi, psikolog, defter | Kesikli bakış çizgisi psikolog gözünden garsona ÇİZ 0.5 sn. Psikolog başı garsonlara 5° döner (0.3 sn). Defterde kalem döngüsü |

- **İkincil hareketler:** Lamba sallanması sönümlenir. Garsonlar durunca NEFES.
- **Kamera:** KAMERA_İTME 1.00→1.05, merkez (960,540)→(1200,560).
- **Geçiş (S6'ya):** İÇERİK_DEĞİŞİMİ. Ön plan (psikolog, etiketler, bakış çizgisi, ikinci garson) SLIDE_OUT. Restoran arka planı kalır.
- **Süreklilik:** Aynı restoran, aynı garson tasarımı S6'da.
- **Kontrol kareleri:** t0.7, t1.9, t3.4.

## S6 · Ödenmemiş siparişler, ödenince unutulur · 4.6 sn

**Amaç:** Önce/sonra karşılaştırması. Aynı garson, aynı poz, iki sütun.

| t | Tetikleyici | Eleman | Hareket |
|---|---|---|---|
| 0.0 | Garsonlar | Sol garson | SLIDE_IN soldan 100 px |
| 0.4 | siparişlerin | 3 sipariş kartı | POP, STAGGER (soldan sağa) |
| 1.0 | ödenmemiş | Kartlar | Üst şerit vurgu rengine 0.2 sn. Her kartta boş madeni para çizgisi (kesikli daire) ÇİZ 0.3 sn, STAGGER |
| 1.5 | hepsini | Üç kart | Eş zamanlı NABIZ (tek) |
| 1.9 | aklında tutuyordu | Bağ çizgileri, garson | Kafadan her karta bağ ÇİZ 0.3 sn eş zamanlı. Garson baş sallar (karakter kuralı) |
| 2.5 | Hesap | Hesap kâğıdı | SLIDE_IN yukarıdan 100 px, ortaya |
| 2.8 | kapanır kapanmaz | Damga | Damga ölçek 1.4→1.0'a 0.15 sn'de iner. İnince SARSINTI(8 px). Tamam rengi, kâğıtta onay işareti |
| 3.0 | ise | Ayırıcı, sağ sütun | Dikey kesikli ayırıcı yukarıdan aşağı ÇİZ 0.4 sn. Sağ garson SLIDE_IN sağdan 100 px (0.5 sn). Hayalet (kesikli) kartlar BELİR, STAGGER |
| 3.3 | hepsini unutuyordu | Sol kartlar, sağ garson | Sol kartlar tamam rengine döner (0.2 sn), sonra sağdaki hayalet konumlarına MOVE (0.6 sn), vardıklarında kesikli kontura ve %30 saydamlığa dönüşür. Bağ çizgileri sönerek kopar. Sağ garson omuz silker (karakter kuralı) |

- **İkincil hareketler:** Kartlar SALLAN (t0.4'ten t3.3'e kadar). Garsonlar NEFES. Hesap kâğıdı hafif eğimli durur.
- **Kamera:** KAMERA_İTME 1.00→1.04, sabit merkez.
- **Geçiş (S7'ye):** SAHNE_KAYMA, t4.1-4.6 aralığında. Zemin çizgisi sabit.
- **Kontrol kareleri:** t1.3, t2.9, t4.0.

## S7 · Beyin ve açık sekme · 3.4 sn

**Amaç:** Metafor: beyin = tarayıcı, işler = açık sekmeler.

| t | Tetikleyici | Eleman | Hareket |
|---|---|---|---|
| 0.0 | Beynin | Beyin, nokta ızgarası | Beyin POP. Izgara BELİR 0.4 sn |
| 0.6 | tamamlanmamış işi | Üç yarım kart | Zarf, sipariş, görev kartları beynin üstünde POP, STAGGER. Çubuklar yarım (%50-60) |
| 1.3 | açık sekme | Kartlar, tarayıcı penceresi | Kartlar MOVE (0.5 sn) ile sekme şeridindeki yerlerine gider, yolda sekme şekline dönüşür (0.2 sn). Pencere çerçevesi sol üstten saat yönünde ÇİZ 0.6 sn. İçi BELİR 0.3 sn. × butonları POP, STAGGER |
| 1.9 | gibi tutar | Bağ çizgileri, beyin | Beyinden her sekmeye kesikli bağ ÇİZ 0.4 sn. Beyin etrafında vurgu rengi parıltı %0→%20 (0.4 sn). Beyin NEFES (periyot 1.6 sn) |
| 2.0 | (öncül) | İmleç | İmleç sağ alttan yavaşça × tuşuna doğru MOVE (0.4 sn, easeInOutCubic) |
| 2.4 | Bitirmeden kapanmaz | İmleç, 1. sekme | Tıklama: × ölçek 0.85 (0.08 sn). Sekme ESNE-SIÇRA. Ardından SARSINTI(4 px, 0.15 sn). İmleç geri çekilir |

- **İkincil hareketler:** Beyin NEFES, parıltı sürekli.
- **Kamera:** KAMERA_İTME 1.00→1.06, beyne.
- **Geçiş (S8'e):** SAHNE_KAYMA, t2.9-3.4 aralığında. Pencere alt kenarı y=860 zemin çizgisi hizasında.
- **Süreklilik:** Sekme kartı ve tarayıcı penceresi S9'da yeniden kullanılır.
- **Kontrol kareleri:** t1.2, t2.0, t2.8.

## S8 · Çözüm: plan yaz · 3.2 sn

**Amaç:** Sade çözüm. Defter shot'un odağı, kart bilerek solgun.

Not: Oda (pencere, zemin, masa) S7→S8 kaymasıyla yerindedir. Defter t1.3'te açılır.

| t | Tetikleyici | Eleman | Hareket |
|---|---|---|---|
| 0.0 | Çözüm basit | Başlık "ÇÖZÜM BASİT." | Harfler POP, aralık 0.05 sn. Sondaki nokta POP + hafif sıçrama. Kontur rengi |
| 0.6 | yapamıyorsan bile | Kişi, kart | Kişi (oturan) POP. Kart %70 saydamlıkla BELİR (0.3 sn), çubuk %60'ta takılı. Kart SALLAN yumuşak (±3 px). Kişi omuzları 10 px düşürür (0.4 sn), iç çeker |
| 1.3 | yarına | Defter, "YARIN", lamba | Defter açılır: sayfa dönüşü 0.4 sn. "YARIN" başlığı POP (küçük). Lamba ışığı ve ışık paralelkenarı 0.4 sn'de yanar (fade) |
| 1.7 | bir plan | 3 satır şablon | Üç kesikli hayalet satır ÇİZ, STAGGER, her biri 0.3 sn |
| 2.0 | yaz | Kalem, satırlar | Kalem (hardal uçlu) girer. Satırlar tek tek YAZ (2.0-2.9), ardışık |

- **İkincil hareketler:** Kart SALLAN, kişi NEFES.
- **Kamera:** KAMERA_İTME 1.00→1.05, merkez deftere (1180,640).
- **Geçiş (S9'a):** Aynı sahne. Yalnızca başlık ve kart SLIDE_OUT. **Kişi, masa ve defter yerinde kalır** (çapa: kişi konumu).
- **Kontrol kareleri:** t0.5, t1.8, t3.0.

## S9 · Sekme kapanır · 1.8 sn

**Amaç:** Sakin çözüm. Tek açık sekme kapanır, gerilim söner.

| t | Tetikleyici | Eleman | Hareket |
|---|---|---|---|
| 0.0 | Beynin | Düşünce balonu, beyin | Balon POP (kuyruk kişinin başına). İçinde mini tarayıcı BELİR, beyin POP (t0.1) |
| 0.4 | sekmeyi | Tek sekme | Şeritte POP, vurgu rengi |
| 0.6 | (öncül) | İmleç | İmleç yaklaşır, MOVE 0.3 sn |
| 0.9 | kapatır | İmleç, sekme, beyin | × tıklanır (0.08 sn). Sekme tamam rengine döner (0.15 sn), ardından genişlikte 1→0 küçülerek kapanır (0.3 sn, easeInOutCubic). Beyin parıltısı vurgu→0 (0.4 sn), beyin NEFES durur |
| 1.4 | (sonuç) | Kişi | Gözler kapalı yaya (0.2 sn), hafif gülümseme, omuzlar 8 px iner, baş 3° eğilir |

- **İkincil hareketler:** t1.5'ten sonra tüm hareket durur (sakin tutuş).
- **Kamera:** KAMERA_İTME 1.00→1.08, balona (900,380). Son 0.3 sn'de yavaşlayarak durur.
- **Bitiş:** t1.8'de video biter.
- **Kontrol kareleri:** t0.3, t1.0, t1.7.

---

## Edit eklentileri (tetikleyiciye bağlı olmayan, yeni nesne olmayan hareketler)

NEFES, SALLAN, su ve çatal döngüleri, lamba sönümlü sallanması, kamera itmeleri, grain, temas gölgeleri, S9'daki sakin tutuş. Bunlar akıcılık ve süreklilik içindir, anlam taşımaz.

## Planın kabul ölçütleri (gözden geçirme turu için)

1. Her tetikleyici tablodaki `t`'de ekranda görünür.
2. Vurgu rengi yalnızca "açık/bitmemiş", tamam rengi yalnızca "kapanmış" bilgide.
3. Bir shot'ta aynı anda okunabilir grup sayısı en çok 5.
4. Geçişlerde zemin çizgisi y=860 sabit.
5. Kontrol karelerinde (her shot'un sonunda listelendi) ekran görüntüsü alınıp plana karşı doğrulanır.
