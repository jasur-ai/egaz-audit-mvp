# Cheklovlar (TZ §10 — yashirilmaydi)

1. **Sintetik ma'lumot.** A1–A8 injection real soxtalashtirishdan soddaroq; model ko'rsatkichlari
   yuqori baho bo'lishi mumkin. Real diapazon PQ-343 integratsiyasidan keyin aniqlanadi.
2. **AQSh/xalqaro kontekst.** TZ'dagi 5–17% oqim noaniqligi kabi qiymatlar chet el sinovlaridan —
   milliy fakt sifatida ishlatilmaydi (⚠️ belgisi bilan).
3. **AE va OCSVM cheklovlari.** AE — driftga sezgir, ko'p ma'lumot talab qiladi; OCSVM — sekin
   (train qism-to'plamda) va kernel sezgir. Ikkalasi MVP ish rejimida ishlatilmaydi.
4. **Nozik turlar.** A5/A7/A8 recall past (0,16/0,08/0,07) — keyingi iteratsiyada feature kengaytirish
   yoki differensial qoldiqlar talab qilinadi.
5. **Alohida domain.** Dehqonchilik/chorvachilik (diffuz manbalar) MVP'dan tashqarida (TZ §10).
6. **Model monitoring.** Hozircha offline: dreyfni aniqlash uchun davriy qayta o'qitish va
   FPR trend monitoringi keyingi bosqich (TZ S8 «Model monitoring» panelining real qismi).
7. **Yuridik jihat.** Tizim yuridik xulosa chiqarmaydi; chiqish — «tekshirishga loyiq signal»
   (anti-mezonlar, TZ §2). Yakuniy qaror vakolatli organ va inson ko'rigida qoladi.
