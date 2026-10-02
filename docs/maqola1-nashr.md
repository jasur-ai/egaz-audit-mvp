# RAQAM ISHONCHSIZ BO'LSA, JAZO ADOLATLIMI? O'LCHOV NOANIQLIGI VA SANKSIYA MANTIG'I O'RTASIDAGI ZIDDIYAT

### WHEN THE NUMBER IS UNRELIABLE, IS THE PENALTY FAIR? MEASUREMENT UNCERTAINTY AND THE LOGIC OF SANCTIONS IN INDUSTRIAL EMISSION MONITORING

---

## Mualliflar va muassasa (to'ldiriladi)

| Maydon | Ma'lumot |
|---|---|
| **Muallif (F.I.Sh.)** | ⟦Familiya Ism Sharif⟧ |
| **Ilmiy daraja / unvon** | ⟦tayanch doktorant / magistrant / mustaqil izlanuvchi⟧ |
| **Ilmiy rahbar** | ⟦F.I.Sh., ilmiy darajasi, lavozimi⟧ |
| **Muassasa** | ⟦Universitet nomi⟧ |
| **Fakultet / kafedra** | ⟦fakultet⟧, ⟦kafedra⟧ |
| **Shahar, mamlakat** | ⟦Toshkent⟧, O'zbekiston |
| **Aloqa (email)** | ⟦muallif@example.uz⟧ |
| **Telefon** | ⟦+998 __ ___ __ __⟧ |
| **ORCID** | ⟦0000-0000-0000-0000⟧ |
| **Manzil (pochta uchun)** | ⟦ko'cha, uy, indeks⟧ |

**UDK** 504.3.054:34.096 · **JEL** Q53, Q58, K32, C18 · **Maqola turi:** tahliliy tadqiqot (policy analysis)
**Kelib tushgan sana:** ⟦__.__.2026⟧ · **Taqrizchi:** ⟦to'ldiriladi⟧

---

## ANNOTATSIYA

Maqolada 2026-yil 1-martdan O'zbekistonda atrof-muhitga ta'sir darajasi bo'yicha I va II toifaga kiritilgan sanoat korxonalarini avtomatik emissiya monitoringi stansiyalari bilan jihozlash majburiyati va shu bilan birga yuzaga kelgan huquqiy muammo ko'rib chiqiladi. Muammoning mohiyati shundaki, o'lchangan raqam endi to'g'ridan-to'g'ri pulga aylanadi: me'yordan oshgan tashlanma uchun kompensatsiya to'lovi belgilanadi, rag'bat rejimida esa to'lovning bir qismi qaytariladi. Ammo o'lchov zanjirining eng katta bo'g'ini — chiqindi gaz sarfi o'lchagichi — xalqaro sinovlarda 5–17%, ayrim holatlarda 20% gacha siljish bergan. Amaldagi tartib esa yagona chegaraga tayanadi va o'lchov noaniqligini huquqiy mezon sifatida tan olmaydi. Natijada chegaraga yaqin turgan korxona uchun bir xil ko'rsatkich ikki xil xulosaga — me'yorda yoki huquqbuzar — olib kelishi mumkin. Tadqiqotda o'lchov zanjiri bo'g'inlari bo'yicha noaniqlik tahlil qilinadi, xatoni jazodan ajratuvchi uch zonali qaror qoidasi (JCGM 106:2012 va ILAC-G8:09/2019 asosida) taklif etiladi, qaror bilan birga beriladigan tushuntirish kartasining 12 maydoni va apellyatsiya oqimining olti bosqichi ishlab chiqiladi. Moliyaviy oqibat hisoblangan misolda ko'rsatiladi: 3% va 10% li ikkita mustaqil noaniqlik yig'indisi 21% kengaytirilgan noaniqlik beradi, besh baravar koeffitsiyent bilan bu bazaviy to'lovning ikki baravarigacha bo'lgan ortiqcha hisob-kitob xavfini keltiradi. Maqola oxirida masshtab masalasi ko'tariladi: 2 335 obyekt va 347 fon stansiyasidan keladigan ma'lumotni qo'lda tekshirish amaliy imkonsiz, shu sababli nazoratsiz anomaliya aniqlash, vaqt qatori dreyfi monitoringi va tushuntiriladigan sun'iy intellekt (XAI) usullari texnologik qatlam sifatida taklif etiladi.

**Kalit so'zlar:** emissiya monitoringi; o'lchov noaniqligi; oqim o'lchagichi; uch zonali qaror qoidasi; kompensatsiya to'lovi; apellyatsiya; anomaliya aniqlash; tushuntiriladigan sun'iy intellekt; O'zbekiston.

---

## ABSTRACT

The paper examines a legal and metrological problem that emerged in Uzbekistan on 1 March 2026, when category I and II industrial enterprises became obliged to install automated emission monitoring stations. From that date a measured value translates directly into money: compensation payments for exceedances of the limit, or a partial refund under the incentive regime. However, the largest source of uncertainty in the measurement chain — the flue-gas flow meter — has shown deviations of 5 to 17 per cent in international tests, and up to 20 per cent in some cases. The current regulatory framework relies on a single threshold and does not recognise measurement uncertainty as a legal criterion, so an identical reading may lead to opposite conclusions: compliance or violation. The study analyses uncertainty link by link, proposes a three-zone decision rule based on JCGM 106:2012 and ILAC-G8:09/2019, develops a twelve-field explanation card that must accompany every penalty decision, and outlines a six-stage appeal flow. A worked calculation shows that two independent uncertainty components of 3 and 10 per cent produce an expanded uncertainty of about 21 per cent, which, multiplied by the statutory coefficient of five, creates a risk of over-assessment almost equal to the base payment itself. The final section addresses scale: with 2 335 regulated objects and 347 background stations, manual verification is not feasible, and unsupervised anomaly detection, time-series drift monitoring and explainable AI are proposed as the technological layer of the same reform.

**Keywords:** emission monitoring; measurement uncertainty; flow meter; three-zone decision rule; compensation payments; appeal; anomaly detection; explainable AI; Uzbekistan.

---

## 1. KIRISH

O'zbekiston sanoat ekologiyasi nazoratida 2026-yil bir necha muhim hujjat bilan kesishgan nuqtaga yetdi. 2025-yil 18-noyabrdagi PQ-343-son qaror I va II toifa korxonalariga fon monitoring stansiyalarini 2026-yil 1-martga qadar o'rnatish va ularni Ekologik monitoring milliy markaziga ulash majburiyatini yukladi; o'rnatmagani uchun kompensatsiya to'lovlari besh baravar oshiriladi [1]. Shu tariqa nazoratning asosiy predmeti hisobot-jadvaldan real vaqtda o'lchanadigan kattalikka o'tdi.

O'lchovning pulga aylanish kanallari bir necha. 2026-yil 4-mayda qabul qilingan O'RQ-1143-son qonun normadan ortiq tashlama uchun kompensatsiya to'lovlarini va jarimalarni sezilarli darajada kuchaytirdi [2, 3]. 2026-yil 28-fevraldagi VM-85-son qaror bilan rag'bat mexanizmi joriy etildi: monitoring stansiyasini o'rnatgan korxona to'lovlardan shakllangan qarzdorlikdan voz kechish huquqini oladi, tozalash uskunalarini ishga tushirganda esa to'lovning bir qismi ikki yil davomida qaytariladi [4]. PF-16-son farmon bilan bu yo'nalish yillik davlat dasturi darajasiga ko'tarilgan [5].

Demak, bitta o'lchov natijasi ayni paytda ham jazo, ham rag'bat manbai. Bu holat o'lchov sifatiga yangi talab qo'yadi: raqam nafaqat aniq, balki tekshiriladigan va e'tiroz bildiriladigan bo'lishi kerak. Amaliyot ko'lami esa katta: 2026-yilda ekologik politsiya 750 ta korxonani tekshirib, tabiatga yetkazilgan zararni 1 trln 386 mlrd so'm miqdorida baholadi va 500 ga yaqin mansabdor shaxsga ma'muriy chora qo'lladi [6]. Birgina 2025-yilda mamlakatda ekologiya sohasida qariyb 59 ming huquqbuzarlik qayd etilgan [7]. Bu raqamlar shuni ko'rsatadiki, o'lchov ishonchi ilmiy-nazariy mavzu emas, bevosita moliyaviy oqibatga ega bo'lgan amaliy masala.

Ilmiy bo'shliq ham shu yerda. Xalqaro adabiyotda uzluksiz emissiya monitoringi (CEMS) ma'lumotlari sifati, anomaliya aniqlash va kalibrovkani nazorat qilish bo'yicha salmoqli ishlar bor [8–11]; xalqaro amaliyotda o'lchov noaniqligini muvofiqlik bahosiga kiritish bo'yicha andozalar ham mavjud [12–14]. Ammo O'zbekistonning yangi huquqiy rejimida bu andozalar hali milliy tartibga singdirilmagan, milliy adabiyotda esa masala deyarli ko'tarilmagan. Maqolaning savoli aynan shundan kelib chiqadi:

> **Chegaraga yaqin turgan korxona uchun o'lchov xatosi normami yoki huquqbuzarlikmi — va buni kim, qanday mezon bilan hal qiladi?**

Tadqiqotning hissasi uch qismdan iborat. Birinchidan, o'lchov zanjiri bo'g'inlari bo'yicha noaniqlik yig'indisi xalqaro manbalar asosida tizimlashtiriladi va xatoning eng ko'p to'planadigan nuqtasi ko'rsatiladi. Ikkinchidan, xatoni jazodan ajratuvchi qaror qoidasi milliy huquqiy rejimga moslashtiriladi. Uchinchidan, bu qoidaning moliyaviy oqibati hisoblab ko'rsatiladi va taklif byudjet jihatidan baholanadi.

Maqolaning tuzilishi quyidagicha. 2-bo'limda o'lchov zanjiri tahlil qilinadi. 3-bo'limda uch zonali qoida va unga biriktirilgan hujjatlar (tushuntirish kartasi, apellyatsiya oqimi) tavsiflanadi. 4-bo'lim pul oqimiga bag'ishlangan. 5-bo'limda qamrov va xarajat masalasi, 6-bo'limda hisoblangan misol, 7-bo'limda texnologik qatlam ko'rib chiqiladi. 8-bo'lim muhokama va cheklovlar, 9-bo'lim xulosa va tavsiyalardan iborat.

---

## 2. O'LCHOV ZANJIRI: NOANISLIQ QAYERDA TO'PLANADI?

### 2.1. Zanjirning tuzilishi

Tashlanmaning o'lchangan massasi uch kattalik ko'paytmasi sifatida shakllanadi: ifloslantiruvchi moddaning kontsentratsiyasi, chiqindi gazning hajmiy sarfi va o'lchov davri. So'ngra bu massa normativ koeffitsiyentlar hamda to'lov stavkalari orqali summaga aylanadi (1-rasm):

**kontsentratsiya × sarf × vaqt → me'yor bilan taqqoslash → koeffitsiyent → to'lov yoki jarima**

![1-rasm](png/K1.png)

*1-rasm. O'lchov xatosining moliyaviy natijaga aylanish zanjiri (muallif ishlanmasi).*

Zanjirning xususiyati shundaki, xato har bir bo'g'inda to'planib, oxirida yagona moliyaviy natijaga jamlanadi. Bo'g'inlarning hissasini bilmasdan turib qaror sifatini baholab bo'lmaydi.

### 2.2. Bo'g'inlar bo'yicha noaniqlik

Xalqaro amaliyotda qayd etilgan qiymatlar 1-jadvalda keltirilgan. Jadvalning o'qilishida bitta metodik noziklik bor: normativ talablar **span** (o'lchov diapazoni) qiymatiga nisbatan beriladi, tadqiqot manbalaridagi 5–17% esa o'sha **o'qish** qiymatiga nisbatan. Bu ikki kattalikni to'g'ridan-to'g'ri qo'shib bo'lmaydi, shuning uchun ular jadvalda alohida ustun mantiqida berilgan.

| Bo'g'in | Noaniqlik / siljish | Manba |
|---|---|---|
| Gaz tahlili (kontsentratsiya) | kalibrovka siljishi ≤2,5% span | EPA PS-2, 40 CFR 60 ilova B [14] |
| CEMS (namuna olish interfeysi bilan) | kalibrovka xatosi ≤5% span | EPA PS-2, 13.2-band [14] |
| Etalon va kalibrovka | ±0,7% | sertifikatlangan etalon gazlar sertifikati |
| **Oqim o'lchagichi (USM, S-probe)** | **5–17%** | Sarunac va boshq., 2004 ⚠️ [8] |
| Uskuna almashtirilganda | ayrim hollarda 20% gacha musbat siljish | o'sha manba ⚠️ [8] |
| Nisbiy aniqlik sinovi (RATA) talabi | ≤10% (oqim monitori), siljish ≤5% FS | Kanada CEMS protokoli ⚠️ [15] |

**1-jadval.** O'lchov zanjiri bo'g'inlaridagi noaniqlik darajalari. ⚠️ belgisi chet el sharoitida olingan qiymatni bildiradi.

1-jadvaldagi qiymatlar O'zbekiston korxonalarida o'tkazilgan o'lchovlar emas. Ular zanjirning qaysi bo'g'inida xato to'planishi mumkinligini ko'rsatuvchi xalqaro tajriba bo'lib, tadqiqotda **tekshirilishi kerak bo'lgan gipoteza** sifatida ishlatiladi. I toifa korxonalarida davriy nisbiy aniqlik sinovlari o'tkazilib, natijalari e'lon qilinsa, milliy diapazon aniqlanadi. Aynan shu maqsadda 9-bo'limda tegishli tavsiya berilgan.

![2-rasm](png/K3.png)

*2-rasm. O'lchov zanjiri bo'g'inlaridagi noaniqlik diapazonlari (adabiyot va xalqaro amaliyot asosida).*

### 2.3. Siljish — xodim xatosi emas, tizim xususiyati

AQShda o'tkazilgan keng ko'lamli sinovlar (Sarunac, Romero, Levy va Bilirgen, Lehigh University Energy Research Center, 2004) oqim o'lchagichlari va suyultiruvchi namuna olish zondlarida ijobiy siljish muntazam uchraganini ko'rsatdi — ayrim holatlarda 20% gacha [8]. Koeffitsiyent haqiqiy qiymatga moslangach, ortiqcha hisob-kitob 15 foiz punktdan ko'proq kamaygan, qoldiq siljish 1–2% darajasida baholangan. Mualliflar bu ishni emissiya savdosidagi moliyaviy yo'qotishlarning oldini olish maqsadida olib borgan.

Bundan kelib chiqadigan xulosa amaliy ahamiyatga ega: bir xil uskuna bilan olingan ikki raqam orasidagi tafovut ko'pincha xodimning beparvoligi emas, **o'lchash tizimining tabiiy siljishi** oqibati. Bu tafovutni tan olmaydigan huquqiy tartib ishonchsizlikni qaror darajasiga ko'taradi.

### 2.4. Normativ talablar: nuqta chegaralar va ularning xato fazosi

O'zbekiston tartibida chang-gaz tozalash uskunalarining samaradorligi ≥99,5%, ≥95% va ≥80% ko'rinishida — **nuqta qiymat** sifatida belgilangan [16]. Xalqaro talablar esa xuddi shu joyda ikkita o'lchovni ajratadi: samaradorlik ko'rsatkichi uskunaning ishlashini bildiradi, noaniqlik esa o'lchangan qiymatning haqiqiy qiymatdan qanchalik chetlanishi mumkinligini ko'rsatadi. Uskuna 95% samaradorlik bilan ishlagan holda ham natijasi 10% noaniqlik bilan o'lchanishi mumkin; biri ikkinchisini inkor etmaydi.

Muhim jihat shundaki, xalqaro andozalarda chegara qiymati ko'pincha ishonch oralig'i bilan birga e'lon qilinadi. Milliy tartibda samaradorlik talabi nuqta sifatida berilgani uchun 10–20% noaniqlik sharoitida qabul qilingan qaror o'zining xato fazosini ko'rsatmaydi. Bu masofa davlat hujjatlarida ham tan olinayotgani kuzatiladi: PF-46-son farmon aynan I va II toifa korxonalarida avtomatik monitoringni alohida maqsad qilib belgilagan [17] — demak, savol endi o'lchov bor-yo'qligida emas, uning ishonchliligida.

---

## 3. HIMOYA MEXANIZMI: XATONI JAZODAN AJRATISH

### 3.1. Uch zonali qaror qoidasi

Taklifning yadrosi — o'lchov natijasini chegara (L) va kengaytirilgan noaniqlik (U) bilan birgalikda baholash. Bu yondashuv JCGM 106:2012 andozasining muvofiqlik bahosi bo'yicha asosiy g'oyasidir [12]; ILAC-G8:09/2019 uni himoya zonasi ko'rinishida amaliyotga tatbiq etadi [13]. Qoidaning shartlari 2-jadvalda qat'iy tengsizliklar bilan berilgan — zonalar orasida ikkilanish qolmasligi uchun.

| Zona | Shart | Huquqiy oqibat |
|---|---|---|
| Yashil | x̄ ≤ L | jazo yo'q; ma'lumot yozib boriladi |
| Sariq | L < x̄ ≤ L + U | jazo yo'q; avtomatik qo'shimcha tekshiruv, korxonaga tavsiya yuboriladi |
| Qizil | x̄ > L + U | jazo + tushuntirish kartasi + e'tiroz bildirish huquqi |

**2-jadval.** Uch zonali qaror qoidasi: shartlar va huquqiy oqibatlar.

Bu konstruksiyada chegara bilan ishonch oralig'i aralashmaydi: yashil zona natijaning me'yor ichidaligini bildiradi, sariq zona xatoning mumkin bo'lgan sohasi chegarani kesib o'tishini tan oladi, qizil zona esa o'lchov aniq ko'rsatgan oshishni qamraydi. Amaldagi tartibda oraliq zona yo'q: VM-783 va unga bog'liq kompensatsiya nizomi talablarni «bajarildi / bajarilmadi» shaklida tartibga soladi, o'lchov noaniqligi esa huquqiy mezon sifatida kiritilmagan [16, 18].

![3-rasm](png/K7.png)

*3-rasm. Uch zonali qaror qoidasi chegara (L) va kengaytirilgan noaniqlik (U) asosida (JCGM 106:2012; ILAC-G8:09/2019).*

Taklifning o'rinliligini nazorat islohoti kuchaytiradi: PF-217-son farmon ekologiya sohasida nazoratni kuchaytirib, 2026-yil 1-apreldan yuridik shaxslarga nisbatan moliyaviy sanksiyalar tartibini joriy etdi [19]. Jazo kuchaygan sharoitda xatoni jazodan ajratadigan himoya zonasi nazorat organining ham, korxonaning ham manfaatiga xizmat qiladi.

### 3.2. Tushuntirish kartasi

Jazo qo'llanilganda qaror bilan birga tushuntirish kartasi berilishi taklif etiladi. Karta o'n ikki maydonni qamraydi: o'lchangan o'rtacha qiymat (x̄), kengaytirilgan noaniqlik (U), me'yor chegarasi (L), qo'llanilgan qaror qoidasi, kalibrovka dalili, laboratoriya va uning akkreditatsiyasi, o'lchash uskunasi, o'lchov sanasi, aniqlangan zona, apellyatsiya yo'li va ma'lumotni mustaqil tekshirish uchun havola. Bu talab ISO/IEC 17025:2017 andozasining 7.8.6-bandi bilan uyg'un: sinov natijalari hisobotida noaniqlik ko'rsatilishi shart [20]. O'zbekiston milliy akkreditatsiya tizimi ILAC o'zaro tan olish kelishuviga 2022-yil 14-sentabrda qo'shilgan, ya'ni bunday hisobotlarni xalqaro darajada tan olish uchun institutsional asos mavjud.

Kartaning amaliy ahamiyati shundaki, u qarorni korxona mustaqil ravishda tekshira oladigan hujjatga aylantiradi. Xuddi shu mantiq boshqa yurisdiksiyalarda ham qo'llanadi: Kanada protokoli siljish belgilangan chegaradan oshsa, keyingi ma'lumotlar tuzatish koeffitsiyenti bilan hisoblanishini talab qiladi — ya'ni tuzatishning o'zi qonuniy jarayon sifatida tan olingan [15].

### 3.3. Apellyatsiya oqimi

E'tiroz bildirish tartibi amaldagi muddatlarga tayanishi mumkin. Taklif etilayotgan oqim olti bosqichdan iborat (4-rasm): xabarnoma (T+0), korxona tushuntirishi (T+2 kun), dastlabki ko'rib chiqish (10 kun), to'lovni shartli ushlab turish, yakuniy xulosa (30 ish kuni, O'RQ-457 bo'yicha) va sud bosqichi [21]. To'lovni to'liq undirib, keyin qaytarish yo'lini tanlash korxona uchun aylanma mablag' riskini tug'diradi; shartli ushlab turish esa pul muzlatilgan holda da'voni saqlab qoladi va ikkala tomon xavfini tenglashtiradi.

![4-rasm](png/K8.png)

*4-rasm. Apellyatsiya oqimining vaqt chizig'i va qo'llaniladigan muddatlar.*

---

## 4. PUL: JAZO VA RAG'BAT BIR ZINAPOYADA BO'LA OLADIMI?

### 4.1. Ikki rejim orasidagi yozilmagan oraliq

Jazo rejimida me'yordan oshgan tashlanma uchun kompensatsiya to'lovi maksimal besh baravargacha oshiriladi [2, 3]. Rag'bat rejimi ikki bosqichga bo'lingan: stansiyani o'rnatgan korxona qarzdorlikdan voz kechish huquqini oladi; tozalash uskunalarini ishga tushirganda esa to'lovlarning bir qismi ikki yil davomida qaytariladi [4]. Shu o'rinda e'tibor talab qiladigan tafovut bor: hujjat matnida ikkinchi bosqich uchun 70 foiz ko'rsatilgan bo'lsa, ommaviy tushuntirishlarda birinchi bosqich uchun 50 foiz, ikkinchisi uchun 70 foiz deb bayon etilgan [22]. Bunday holatda rasmiy matn ustuvor bo'lishi kerak, ammo ommaviy tushuntirishdagi nomuvofiqlik korxona uchun investitsiya qarorini qiyinlashtiradi.

Ikki rejim orasidagi masofa katta, lekin **oraliq holatlar yozilmagan**: 50% va 70% orasidagi farq qanday mezonga bog'liq, ikki yillik muddat qaysi kundan boshlanadi, tozalash uskunasi qaysi samaradorlik darajasidan «o'rnatilgan» hisoblanadi — bu savollarga hujjatlarda aniq javob yo'q.

Atamalarni ham ajratish zarur. Rag'bat rejimi **to'lovga** nisbatan imtiyoz beradi: undirilishi mumkin bo'lgan kompensatsiya to'lovidan voz kechiladi yoki uning bir qismi qaytariladi. **Jarima esa bu imtiyozga kirmaydi** — u ma'muriy jazo sifatida o'z kuchida qoladi va faqat qonunda ko'rsatilgan asoslar bo'yicha bekor qilinishi mumkin. Ommaviy tushuntirishlarda bu ikki narsa ko'pincha bir gapda aytiladi va korxonada «jarimani qaytarib olaman» degan noto'g'ri tasavvur shakllanadi; hujjat matni bunday o'qishga asos bermaydi.

### 4.2. Vaqt assimetriyasi

To'lovlar rejasidagi raqamlar masalani yorqin ko'rsatadi (7-rasm). 2025-yil uchun sohaviy jamg'arma 900 mlrd so'm hajmida rejalashtirilgan edi; 2026-yil uchun reja 548 mlrd so'm, amalda birinchi yarim yillikda 274 mlrd so'm tushgan [23, 24]. Bu yerda ziddiyat yo'q: 274 mlrd — yarim yillik ko'rsatkich, uni yillikka keltirilsa 274 × 2 = 548 mlrd bo'ladi, bu esa e'lon qilingan yillik reja bilan mos tushadi. Taqqoslashda xatolik faqat davrlar aralashtirilganda yuzaga keladi.

Pul oqimining ikkinchi tomoni vaqtga sezgir: jazo qarori tez qo'llanadi, to'lovning qaytarilishi esa ikki yilga cho'ziladi (6-rasm). Diskontlangan qiymatda bu rag'batni sezilarli zaiflashtiradi. Shu sababli dastlabki olti oyda tezlashtirilgan qaytarish tartibi taklif etiladi: byudjet uchun neytral, korxona uchun esa investitsiya qarorini tezlashtiruvchi chora.

![6-rasm](png/K9.png)

*6-rasm. Vaqt assimetriyasi: jazo darhol qo'llanadi, kompensatsiya qaytarilishi ikki yilga cho'ziladi.*

![7-rasm](png/K6.png)

*7-rasm. Sohaviy jamg'arma hajmi: 2025-yil rejasi, 2026-yil rejasi va birinchi yarim yillik natijasi.*

---

## 5. QAMROV VA XARAJAT

### 5.1. Qamrov raqamlari

VM-783-son qaror bilan I toifa bo'yicha 663 ta, II toifa bo'yicha 1 672 ta obyekt qamrab olinadi — jami 2 335 ta; viloyat va tumanlarda fon monitoringi uchun 347 ta kichik avtomatik stansiya o'rnatilishi belgilangan [16, 25]. Sanoat tomonidagi amaliy natijalar quyidagicha: 44 ta korxonada 69 ta avtomatik stansiya ishga tushirilgani qayd etilgan [26]; 2026-yil sentabrga kelib «Zamin» fondi ko'magida 28 ta HORIBA komplekti o'rnatilgani xabar qilingan [27]; I toifadagi 9 ta sement zavodida avtomatik kuzatuv stansiyalari ish boshlagan [28].

Bu raqamlardan oddiy nisbat kelib chiqadi: stansiya o'rnatilgan korxonalar sonini toifa obyektlariga bo'lsak, **44 / 2 335 ≈ 1,9%** (muallif hisob-kitobi). Ko'rsatkich qamrov hali boshlang'ich bosqichda ekanini bildiradi. Tekshiruv usuli bilan yopilayotgan qism esa yillik yuzlab korxona hajmida: 2026-yilda 750 ta korxona tekshirilgan [6]. Qamrov tez o'sayotgani holda o'lchov sifati mexanizmlari shakllanmagan — maqolaning asosiy dalili shu.

![8-rasm](png/K5.png)

*8-rasm. Qamrov ko'rsatkichlari: obyektlar soni, tekshiruvlar va o'rnatilgan stansiyalar.*

### 5.2. Xarajat tuzilishi

«Bunday tizim juda qimmat» degan e'tirozni tekshirish uchun xarajatni to'rt blokka ajratish maqsadga muvofiq: uskuna (tahlil qurilmasi, oqim o'lchagichi, kalibrovka gazlari); o'rnatish va integratsiya (quvurga moslash, elektr ta'minoti, ma'lumot uzatish, platformaga ulash); yillik xizmat (tekshirish, kalibrovka, ehtiyot qismlar — xalqaro amaliyotda uskuna qiymatining 5–15% i); mustaqil tekshiruv (davriy nisbiy aniqlik sinovi va qayta o'lchov).

Xalqaro bozor narxlari diapazoni keng: CEMS uchun 120–350 ming dollar, havo sifati monitoring stansiyalari uchun 150–250 ming dollar, chang monitoringi uchun 20–50 ming dollar, etalon uskunalar uchun 15–40 ming dollar [29]. O'zbekistondagi shartnoma summalari ochiq xarid tizimlarida to'liq oshkor etilmagani uchun bu raqamlar faqat yo'naltiruvchi; milliy taqqoslash uchun ochiq reyestr zarur.

![9-rasm](png/K4.png)

*9-rasm. CEMS va monitoring uskunalarining xalqaro narx diapazonlari (logarifmik shkala; vendor sahifalari, 2026).*

### 5.3. Choraklik «Aniqlik hisoboti»

Tizim o'z ishining natijasini ham o'lchashi kerak. Taklif: har chorakda besh ko'rsatkich e'lon qilinadi (10-rasm) — umumiy signallar soni, sariq zona ulushi, qayta o'lchov natijalari, e'tirozlar statistikasi va kalibrovkalar holati. Qizil signallarning kamida 5 foizi ILAC o'zaro tan olish doirasidagi mustaqil laboratoriyada qayta o'lchanadi. Bu ko'rsatkichlar nazorat organining o'z xatosini ko'rsatishga tayyorligini bildiradi va jamoatchilik ishonchini mustahkamlaydi.

![10-rasm](png/K10.png)

*10-rasm. Choraklik «Aniqlik hisoboti» uchun besh ochiq ko'rsatkich.*

---

## 6. HISOBLANGAN MISOL: NOANIQLIK QANDAY SUMMAGA AYLANADI?

Quyidagi hisob-kitob muallifga tegishli bo'lib, o'lchov noaniqligining moliyaviy oqibatini ko'rsatish maqsadida keltiriladi. Gaz tahlilining nisbiy standart noaniqligi 3%, oqim o'lchagichiniki esa 1-jadvaldagi diapazonning o'rtasiga yaqin qiymat sifatida 10% deb olaylik. Bu ikki komponent mustaqil, shuning uchun yig'indi noaniqlik kvadratlar yig'indisining ildizi bilan hisoblanadi:

- u = √(3² + 10²) = √109 ≈ **10,4%**
- kengaytirilgan noaniqlik (k = 2): U = 2 × 10,4 ≈ **21%**

Demak, o'lchov natijasi me'yor chegarasida (x̄ = L) bo'lsa ham, haqiqiy qiymat taxminan 0,79L dan 1,21L gacha oraliqda bo'lishi mumkin. Amaldagi yagona chegarali tartibda bu oraliqning yuqori qismi huquqbuzarlik sifatida qayd etiladi.

Moliyaviy oqibatni koeffitsiyent orqali ko'rsatish mumkin. O'RQ-1143 bo'yicha kompensatsiya to'lovi besh baravargacha oshirilgani uchun chegarada turgan korxona uchun asossiz hisoblanishi mumkin bo'lgan to'lov miqdori taxminan

**5 × 0,21 ≈ 1,05**

ya'ni bazaviy to'lovning bir baravariga teng. Boshqacha aytganda, korxona me'yor ichida turib ham ikki baravar to'lov bilan yuzlashish ehtimoliga ega bo'ladi.

Hisobning real masshtabini bir misol ko'rsatadi: 2026-yil may oyida Muborak gazni qayta ishlash zavodiga ekologik qonunbuzarliklar uchun 10 mlrd 834 mln so'm miqdorida qo'shimcha kompensatsiya belgilangani e'lon qilindi [30, 31]. Bunday summalarda 20% noaniqlik qariyb 2,2 mlrd so'mga teng (10 834 × 0,20 ≈ 2 167 mln so'm). Har bir holatda noaniqlikning haqiqiy qiymati o'lchash tizimiga bog'liq; maqsad aniq raqamni talab qilish emas, **noaniqlik hisobga olinmagan qarorning moliyaviy narxini ko'rsatish**.

Bu hisob PF-46 maqsadlari fonida o'qilishi kerak: «Toza havo» loyihasi atmosferaga tashlanmalarni 10,5 foizga kamaytirishni maqsad qilib qo'ygan [17]. Bunday maqsadni faqat xatosi e'lon qilinadigan o'lchov bilan boshqarish mumkin — aks holda natija ham, hisobot ham tekshirilmaydigan bo'lib qoladi.

---

## 7. TEXNOLOGIK QATLAM: NEGA AVTOMATLASHTIRISH ZARUR, CHEGARASI QAYERDA?

Taklif etilayotgan uch zonali tizim ma'lumot oqimini avtomatik qayta ishlashni nazarda tutadi. Masshtab ham shuni talab qiladi: bir tomonda O'zbekistonning 2 335 obyekti va 347 fon stansiyasi, ikkinchi tomonda xalqaro amaliyot — Xitoy milliy uglerod savdo tizimi kengayishdan keyin 3 680 obyektni qamraydi (2 087 energetika, 962 sement, 232 metallurgiya, 97 alyuminiy) va mamlakat emissiyalarining 60 foizdan ortig'ini tashkil qiladi [32]; Yevropa Ittifoqi tizimi qariyb 10 ming statsionar qurilmani qamraydi (ICAP hisobida 8 704 qurilma, 2024) [33]. Bu hajmdagi tizimlarda ko'rsatkichlarni qo'lda tekshirish amalda mumkin emas. Yo'nalish milliy kun tartibida ham ustuvor: PQ-358 sun'iy intellekt strategiyasi va VM-425 ustuvor AI loyihalari ro'yxati davlat organlariga shu yo'nalishda joriy etishni belgilaydi [34].

Zonalar tizimiga to'rtta aniq vazifa to'g'ri keladi (3-jadval).

| Vazifa | Texnika | Nega aynan shu |
|---|---|---|
| Yuzlab obyekt orasidan birinchi navbatda tekshirilishi keraklilarini ajratish | Isolation Forest / One-Class SVM — nazoratsiz anomaliya aniqlash | Yorliqlangan «buzilish» holatlari yo'q; nazoratsiz usullar shu sharoit uchun ishlab chiqilgan [9] |
| Kalibrovka siljishi va uskuna eskirishi kabi sekin dreyfni aniqlash | Vaqt qatori dekompozitsiyasi (STL) + qoldiq chegarasi; LSTM-autoencoder | Dreyf nuqta-anomaliya emas: trend va mavsumiylikdan ajratilgan qoldiqda qidiriladi [10, 11] |
| Tushuntirish kartasida «nega bu qaror chiqdi»ni ko'rsatish | Tushuntiriladigan AI (XAI): SHAP qiymatlari yoki xususiyat ahamiyati | Karta aynan shu tamoyilni amalga oshiradi — qaror asosi raqamli dalil bilan ochiladi |
| O'lchovni ishlab chiqarish hajmi va energiya balansi bilan solishtirish | Ko'p manbali ma'lumot sintezi va o'zaro tekshiruv | Mustaqil manbalar birgalikda ma'lumotni yashirishni qimmatlashtiradi |

**3-jadval.** Uch zonali qoidaga mos texnologik vazifalar va usullar.

Xalqaro adabiyot bu yo'nalishda tekshirilgan natijalar beradi: Xu va boshqalar (2025) kimyoviy sanoat parki misolida 17 modelni sinab, CEMS ma'lumotlaridagi rejim o'zgarishlarini 90% ishonch darajasida aniqlagan, shundan 24 tasi nazorat yozuvlariga mos kelgan [10]; Song va boshqalar (2025) kalibrovka, bo'shliqlarni to'ldirish va anomaliya aniqlashni yagona ramkaga birlashtirgan [11]; Wu va boshqalar (2026) sement zavodlarida 2% va undan yuqori buzilishlarni 90% dan yuqori aniqlikda topgan, yolg'on signal darajasi 3% dan past bo'lgan [35]. Shu bilan birga, usullarning chegarasi ham aniq: mashina modeli qarorni **asoslavdi**, lekin huquqiy javobgarlikni o'z zimmasiga olmaydi. Shuning uchun sariq va qizil zonalar bo'yicha yakuniy xulosa har doim inson ekspertizasi va tushuntirish kartasi orqali rasmiylashtiriladi.

---

## 8. MUHOKAMA VA CHEKLOVLAR

**Noaniqlikni tan olish nazoratni bo'shashtiradimi?** Amaliyot buni tasdiqlamaydi: sariq zona jazoni bekor qilmaydi, u tekshiruvni ko'paytiradi. Xatoni jazodan ajratish jarima tizimining o'zini ishonchli qiladi — bugungi holatda e'tiroz bildirish uchun asos korxonada emas, hujjatda bo'lishi kerak.

**Xatoni yashirish xavfi qanday kamaytiriladi?** Vosita — qarama-qarshi signal: hisoblangan massa ishlab chiqarish hajmi, xom ashyo iste'moli va energiya balansi bilan solishtiriladi. Bu nisbatlar o'lchov uskunasidan mustaqil bo'lgani uchun birgalikda yashirishni qimmatlashtiradi. Tashqi mustaqil kanal ham bor: ochiq sun'iy yo'ldosh ma'lumotlari asosida emissiya hisobini tekshirish usullari rivojlanmoqda, ular bugungi kunda milliy nazorat tizimlarida yordamchi dalil sifatida qo'llaniladi.

**Reyting va siyosiylashuv.** Korxonalar kesimidagi bir martalik reyting tez siyosiylashadi va ko'rsatkichlar rasmiyatchilikka aylanishi mumkin. Shuning uchun metodika oldindan e'lon qilinishi va baholash ko'rsatkichlarning yaxshilanish **dinamikasi** bo'yicha olib borilishi kerak: reyting yakuniy hukm emas, o'zgarish tendensiyasi sifatida o'qilishi lozim.

**Xarajat va bosqichlash.** To'rt blokli xarajat tuzilmasi bosqichma-bosqich o'rnatishning byudjet asosi bo'lishi mumkin: avval I toifa va yuqori emissiyali tarmoqlar (energetika, sement, metallurgiya), keyin qolgan obyektlar. Bu mantiq davlat hujjatlariga ham mos: PF-46 aynan I va II toifa korxonalarini birinchi navbatga qo'ygan, PQ-343 esa stansiyalarni 2026-yil 1-martga qadar o'rnatishni belgilagan [1, 17].

**Tadqiqotning cheklovlari.** Birinchidan, 1-jadvaldagi noaniqlik qiymatlari xalqaro manbalardan olingan; O'zbekiston korxonalari bo'yicha milliy o'lchovlar hozircha e'lon qilinmagan. Ikkinchidan, uskuna narxlari bo'yicha milliy shartnoma ma'lumotlari ochiq emas, shuning uchun xarajat bahosi yo'naltiruvchi xarakterda. Uchinchidan, hisoblangan misolda noaniqlik komponentlari adabiyotdagi tipik qiymatlar asosida olindi; har bir korxona uchun haqiqiy qiymat o'lchash tizimiga bog'liq. Bu cheklovlar tadqiqotning xulosasini o'zgartirmaydi, lekin uni **aniq raqam emas, mexanizm taklifi** sifatida o'qish zarurligini bildiradi.

---

## 9. XULOSA VA TAVSIYALAR

O'lchov ishonchi bugungi O'zbekistonda texnik masala emas, moliyaviy va huquqiy masala. Tashlanma uchun to'lovlar besh baravargacha oshirilgan, rag'bat mexanizmi joriy etilgan, nazorat esa 2 335 obyektni qamraydi — bunday sharoitda o'lchov zanjiridagi 20% atrofidagi noaniqlik bevosita millionlab so'mlik qarorlarga ta'sir qiladi. Tadqiqot quyidagi amaliy tavsiyalarni beradi:

1. **Uch zonali qaror qoidasini normativ hujjatga kiritish** — chegara bilan birga kengaytirilgan noaniqlik hisobga olinsin (JCGM 106 va ILAC-G8 asosida).
2. **Har bir jazo qaroriga tushuntirish kartasini ilova qilish** — ISO/IEC 17025 7.8.6-bandiga mos holda noaniqlik va qaror asosi ko'rsatilsin.
3. **I toifa korxonalarida davriy nisbiy aniqlik sinovlarini (RATA) joriy etish va natijalarini yillik e'lon qilish** — milliy noaniqlik diapazoni shu asosda aniqlanadi.
4. **Rag'bat shartlaridagi yozilmagan oraliqlarni to'ldirish** — 50%/70% farqining mezoni, qaytarish muddatining boshlanish nuqtasi va «o'rnatilgan uskuna» ta'rifi hujjatlarda aniqlashtirilsin.
5. **Qayta o'lchovni mustaqil laboratoriyalarda tashkil qilish** — qizil signallarning kamida 5 foizi ILAC doirasidagi laboratoriyada tekshirilsin.
6. **Choraklik «Aniqlik hisoboti» e'lon qilish** — besh ko'rsatkich jamoatchilikka ochiq bo'lsin.
7. **Avtomatlashtirish qatlamini bosqichma-bosqich joriy etish** — nazoratsiz anomaliya aniqlash va tushuntiriladigan AI usullari qaror qabul qiluvchini almashtirmasdan, uni qo'llab-quvvatlovchi vosita sifatida ishlatilsin.

Bu choralar byudjet nuqtai nazaridan qo'shimcha xarajat talab qilmaydi: ular mavjud o'lchov ma'lumotlarini hisobot va qaror hujjatlarida to'g'ri aks ettirish bilan bog'liq. Ammo ularning oqibati katta — o'lchov ishonchi oshsa, sanktsiya ham, rag'bat ham o'z maqsadiga yetadi.

---

## Muallif hissasi, manfaatlar va ma'lumotlar

**Muallif hissasi.** ⟦F.I.Sh.⟧ — tadqiqot kontseptsiyasi, o'lchov zanjiri tahlili, uch zonali qoidaning ishlab chiqilishi, hisob-kitoblar, matnni yozish. ⟦Ilmiy rahbar F.I.Sh.⟧ — uslubiy rahbarlik, natijalarni tekshirish va matnni ilmiy tahrir qilish.

**Manfaatlar to'qnashuvi.** Mualliflar tomonidan manfaatlar to'qnashuvi e'lon qilinmaydi. Tadqiqot hech qanday sanoat guruhi yoki davlat organi buyurtmasi asosida bajarilmagan.

**Moliyalashtirish.** ⟦Tadqiqot o'z hisobidan bajarilgan / grant raqami⟧.

**Ma'lumotlarning mavjudligi.** Maqolada keltirilgan barcha rasmiy hujjatlar, normativ manbalar va media ma'lumotlariga havolalar 9-bo'limdagi ro'yxatda berilgan. Muallif hisob-kitoblari (5.1, 5.2, 6-bo'limlar) matnda alohida belgilangan va ular 9-bo'limdagi 8-tavsiya asosida tekshirilishi mumkin.

**Etika bayoni.** Tadqiqot ochiq manbalar va rasmiy hujjatlarga asoslanadi; korxonalar bo'yicha shaxsga oid yoki maxfiy ma'lumotlar ishlatilmagan.

**Rahmatnoma.** ⟦ixtiyoriy⟧.

---

## 10. FOYDALANILGAN MANBALAR

*Dalillar uch darajaga ajratilgan: **R** — rasmiy hujjatlar va davlat organlari ma'lumotlari; **A** — xalqaro andozalar, regulyator talablari va hakamlik ko'rigidan o'tgan tadqiqotlar; **M** — media va ochiq manbalar. Barcha havolalar 2026-yil oktabr holatida tekshirilgan.*

**R — Rasmiy hujjatlar va davlat ma'lumotlari**

1. PQ-343-son qaror, 18.11.2025 — ekologiya va iqlim o'zgarishi sohasidagi chora-tadbirlar; monitoring stansiyalarini 01.03.2026 ga qadar o'rnatish va integratsiya talabi. https://lex.uz/uz/docs/-7847341
2. O'RQ-1143-son qonun, 04.05.2026 — ekologik huquqbuzarliklar uchun javobgarlikni kuchaytirish. https://lex.uz/docs/8169998
3. gazeta.uz, 05.05.2026 — O'RQ-1143: yuridik shaxslarga nisbatan moliyaviy sanksiyalar. https://www.gazeta.uz/oz/2026/05/05/ekologiya/
4. VM-85-son qaror, 28.02.2026 — atrof-muhitga salbiy ta'sirni kamaytirish harakatlarini rag'batlantirish nizomi. https://lex.uz/uz/docs/-8068163
5. PF-16-son farmon, 30.01.2025 — «O'zbekiston-2030» strategiyasiga oid davlat dasturi. https://lex.uz/docs/-7369703
6. Sputnik O'zbekiston, 05.08.2026 — 750 korxona tekshiruvi: 1 trln 386 mlrd so'm zarar. https://oz.sputniknews.uz/20260805/uzbekistan-korxona-ekologiya-zarar-59509079.html
7. gazeta.uz, 01.05.2026 — ekologiya sohasida 2025-yilda qariyb 59 ming huquqbuzarlik. https://www.gazeta.uz/oz/2026/05/01/eco/
8. Sarunac, N., Romero, C.E., Levy, E.K., Bilirgen, H. (2004). Factors affecting CEM measurement accuracy and recommendations for improvement. Lehigh University Energy Research Center, AQSh; OSTI 20501708.
9. Nassif, A.B., Abu Talib, M., Nasir, Q., Dakalbab, F.M. (2021). Machine learning for anomaly detection: a systematic review. *IEEE Access*, 9, 78658–78700. https://doi.org/10.1109/ACCESS.2021.3083060
10. Xu, Z., Shi, X., Shu, W., Xin, Y., Zan, X., Si, Z., Cheng, J. (2025). Machine learning classifiers to detect data pattern change of continuous emission monitoring system. *Environment International*, 201, 109594. https://doi.org/10.1016/j.envint.2025.109594
11. Song, Y., Luo, X., Lu, Y., Qian, J., Zhang, W., Liu, L., Huang, J., Zhao, X., Zhang, D. (2025). Improving the data quality of CO₂ continuous emissions monitoring systems. *Environmental Impact Assessment Review*, 115, 108037. https://doi.org/10.1016/j.eiar.2025.108037
12. JCGM 106:2012 — Evaluation of measurement data: The role of measurement uncertainty in conformity assessment. BIPM.
13. ILAC-G8:09/2019 — Guidelines on decision rules and statements of conformity. ILAC.
14. EPA (AQSh), 40 CFR 60, ilova B — Performance Specification 2: kalibrovka siljishi ≤2,5% span, kalibrovka xatosi ≤5% span. https://www.ecfr.gov/current/title-40/chapter-I/subchapter-C/part-60
15. Environment Canada — CEMS protokoli (RATA ≤10%, siljish ≤5% FS; tuzatish tartibi).
16. VM-783-son qaror, 25.11.2024 — sanoat korxonalarining atrof-muhitga salbiy ta'sirini kamaytirish chora-tadbirlari (1-, 2-, 3-ilovalar: 347 stansiya, toifalar, samaradorlik talablari). https://lex.uz/uz/docs/-7233437
17. PF-46-son farmon, 25.03.2026 — «Toza havo» umummilliy loyihasi: tashlanmalarni 10,5% kamaytirish, I/II toifa monitoringi. https://lex.uz/uz/docs/-8101201
18. 202-son Nizom — kompensatsiya to'lovlari tartibi (201-band: koeffitsiyentlar; 301-band: rag'bat shartlari). https://lex.uz/uz/docs/-5367873
19. PF-217-son farmon, 18.11.2025 — ekologiya sohasida nazoratni kuchaytirish; 01.04.2026 dan moliyaviy sanksiyalar tartibi. https://lex.uz/uz/docs/-7847353
20. ISO/IEC 17025:2017 — sinov va kalibrovka laboratoriyalari kompetentligiga qo'yiladigan talablar, 7.8.6-band.
21. O'RQ-457-son qonun, 08.01.2018 — «Ma'muriy tartib-taomillar to'g'risida»: murojaat va apellyatsiya muddatlari (30 ish kuni). https://lex.uz/docs/-3492199
22. gazeta.uz, 02.03.2026 — VM-85 nizomi: qarzdorlikdan voz kechish va to'lovning bir qismini qaytarish shartlari. https://www.gazeta.uz/oz/2026/03/02/eco/
23. gazeta.uz, 16.09.2026 — 2026-yil birinchi yarmida sohaviy jamg'armaga 274 mlrd so'm. https://www.gazeta.uz/oz/2026/09/16/budget-2026/
24. uza.uz, 15.09.2026 — davlat byudjetining yarim yillik ijrosi: ekologiya yo'nalishi. https://uza.uz/oz/posts/davlat-byudjetining-yarim-yillikdagi-ijrosi-qanday-baholandi_909226
25. kun.uz, 25.11.2025 — 347 ta fon stansiyasi va «Air Monitoring Uzbekistan» platformasi. https://kun.uz/news/2025/11/25/toshkentda-ekologik-vaziyatni-yaxshilash-uchun-maxsus-komissiya-tuzildi
26. Senat ma'lumoti (SQ-844-IV), 20.12.2023 — 44 korxonada 69 avtomatik stansiya. https://lex.uz/docs/-6733055
27. Anhor, 08.09.2026 — «Zamin» fondi ko'magida 28 ta HORIBA stansiyasi. https://anhor.uz/uzl/ekologiya/ozbekistonda-havo-sifati-monitoring-kengaytirish
28. uza.uz, 29.11.2025 — I toifadagi 9 sement zavodida avtomatik kuzatuv stansiyalari ishga tushgani.
29. Applus, Clarity.io, ESEGAS, Accio — CEMS va havo monitoringi uskunalarining xalqaro narx diapazonlari (2026-yil ochiq sahifalari; yo'naltiruvchi ma'lumot).
30. gazeta.uz, 13.05.2026 — Muborak GQIZga 10 mlrd 834 mln so'm qo'shimcha kompensatsiya. https://www.gazeta.uz/oz/2026/05/13/muborak/
31. spot.uz, 13.05.2026 — Muborak GQIZ: 10,8 mlrd so'm kompensatsiya. https://www.spot.uz/oz/2026/05/13/muborak/
32. ICAP (2025); gov.cn, 27.03.2025 — Xitoy milliy uglerod savdo tizimining kengayishi: 3 680 obyekt. https://icapcarbonaction.com/en/news/china-officially-expands-national-ets-cement-steel-and-aluminum-sectors
33. Yevropa Komissiyasi — Scope of the EU ETS: qariyb 10 000 statsionar qurilma; ICAP hisobida 8 704 qurilma (2024). https://climate.ec.europa.eu/eu-action/carbon-markets/eu-emissions-trading-system-eu-ets/scope-eu-ets_en
34. PQ-358-son qaror, 14.10.2024 — sun'iy intellekt texnologiyalarini rivojlantirish strategiyasi; VM-425-son qaror, 10.07.2025 — ustuvor AI loyihalari ro'yxati.
35. Wu, T., Fan, J. va boshq. (2026). An improved carbon dioxide monitoring method related to China's carbon emissions trading system in cement plants. *Processes*, 14(3), 554. https://doi.org/10.3390/pr14030554
36. «Issiqxona gazlarining chiqarilishini cheklash to'g'risida» qonun, 07.07.2025 (kuchga kirishi 09.01.2026). https://www.gazeta.uz/oz/2025/07/09/greenhouse/
37. UNFCCC — Uzbekistan NDC 3.0 (2025): 2035-yilga emissiya intensivligini 2010-yilga nisbatan 50% ga kamaytirish. https://unfccc.int/sites/default/files/2025-11/Uzbekistan%20Third%20NDC.pdf

---

## ILOVA A. Rasmlar ro'yxati

1-rasm — o'lchov xatosining moliyaviy natijaga aylanish zanjiri · 2-rasm — bo'g'inlar bo'yicha noaniqlik diapazonlari · 3-rasm — uch zonali qaror qoidasi · 4-rasm — apellyatsiya oqimi · 5-rasm — jazo va rag'bat rejimlari (ilovada) · 6-rasm — vaqt assimetriyasi · 7-rasm — sohaviy jamg'arma hajmi · 8-rasm — qamrov ko'rsatkichlari · 9-rasm — xalqaro narx diapazonlari (ilovada) · 10-rasm — choraklik aniqlik hisoboti.

## ILOVA B. Nashr variantlari

**Qisqartirilgan shakl (konferensiya tezisi, 4–6 bet).** 2, 3.1, 6 va 9-bo'limlar saqlanadi; 5 va 7-bo'limlar bir abzatsga siqiladi.

**To'liq shakl (jurnal maqolasi).** Joriy tuzilma. Hajmi: ~3 300 so'z, 3 jadval, 10 rasm.

**Sarlavha alternativalari.** «Chegaradagi korxona: o'lchov xatosi va huquqiy oqibat»; «2 335 obyekt, 5–17% noaniqlik: emissiya nazoratining ishonch masalasi».

**Nashr etishdan oldingi tekshiruv ro'yxati.** (1) muallif va rahbar ma'lumotlari to'ldirilsin; (2) UDK/JEL tahririyat talabiga moslashtirilsin; (3) 1-jadvaldagi xalqaro qiymatlar milliy RATA natijalari bilan yangilansin (mavjud bo'lganda); (4) rasmlar 300 dpi formatda taqdim etilsin; (5) havolalar tahririyat uslubiga (GOST yoki APA) o'tkazilsin.
