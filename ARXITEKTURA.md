# LMS — arxitektura va domen hujjati

> Bu hujjat tizim analitigi ko'zi bilan yozilgan. Kod yozishdan oldin o'qing — nima uchun qurayotganingizni tushunmasdan, qanday qurishni bilib bo'lmaydi.

## 1. Dastur g'oyasi

Bir gap bilan: **o'quv markazning butun kundalik hayoti — kurslar, guruhlar, darslar, davomat, bilim nazorati va rag'bat — bitta tizimda, bitta haqiqat manbasida yashaydi.**

Bugun bu ma'lumotlar daftarda, Excelda va Telegramda sochilib yotadi. Kim qaysi guruhda, bugun kim keldi, kim normativni topshirdi, kimga qancha coin berildi — hech kim aniq bilmaydi. LMS shu tartibsizlikni tugatadi: har savolning javobi tizimda bor va u yagona.

## 2. Maqsad va vazifalar

### Biznes maqsadlar

1. O'quv jarayonini shaffof qilish — ota-ona ham, direktor ham, o'quvchi ham bir xil raqamlarni ko'radi
2. O'qituvchini qog'ozbozlikdan ozod qilish — davomat va baholash 2 daqiqada
3. O'quvchini o'qishga qiziqtirish — coin, reyting, do'kon orqali o'yin elementi
4. Tarixni yo'qotmaslik — kim qachon keldi-ketti, nima oldi-berdi, hammasi izli

### Tizim vazifalari

- Kurs → modul → dars ierarxiyasini yuritish
- Guruhlar, a'zolik tarixi va haftalik jadvalni boshqarish (xona to'qnashuvisiz)
- O'tilgan darsni qayd qilish va davomat belgilash
- Normativ (dars savollari) topshirish va qo'lda baholash aylanmasini yuritish
- Coin hisobini tranzaksiyalar orqali yuritish, do'kon va reytingni ta'minlash
- Yangiliklar chop etish

## 3. Foydalanuvchi rollari

| Rol | Kim | Nima qiladi |
|---|---|---|
| **Admin** | Markaz boshqaruvchisi | Hamma narsa: userlar, kurslar, sozlamalar |
| **Teacher** | O'qituvchi | O'z guruhlari: dars qayd, davomat, normativ tekshirish, coin berish |
| **Mentor** | Yordamchi | Guruhga biriktiriladi, o'quvchilarga yordam beradi |
| **Student** | O'quvchi | O'qiydi: normativ topshiradi, natijasini, balansini, reytingini ko'radi, do'kondan oladi |

Texnik jihatdan hammasi bitta `CustomUser`, farqi — `role` fieldi. Teacher va Student qo'shimcha ma'lumotlari alohida profil modellarida.

## 4. Domen lug'ati

Jamoada hamma bir xil so'zlashsin. Kodda ham aynan shu atamalar ishlatiladi.

| Atama | Model | Ma'nosi |
|---|---|---|
| Kurs | `Course` | O'quv dasturi (masalan "Python asoslari") |
| Modul | `Module` | Kursning bobi, tartib raqamli |
| Dars (mavzu) | `Lesson` | O'quv rejadagi mavzu. Hamma guruh uchun bir xil |
| Guruh | `Group` | Kursni birga o'qiyotgan jamoa: o'qituvchi, boshlanish sanasi |
| A'zolik | `GroupStudent` | O'quvchining guruhdagi tarixi: qachon kirdi, qachon chiqdi |
| Jadval qatori | `GroupSchedule` | Haftalik shablon: "P-01 dushanba 14:00-16:00, 1-xona" |
| O'tilgan dars | `GroupLesson` | Konkret guruhda konkret SANADA bo'lib o'tgan dars |
| Davomat | `Attendance` | O'tilgan darsdagi holat: keldi / kechikdi / kelmadi |
| Normativ | `Normativ` | Darsga biriktirilgan savollar to'plami |
| Javob | `NormativAnswer` | O'quvchining yozma javobi + o'qituvchi bahosi |
| Tranzaksiya | `CoinTransaction` | Coin harakati: +5 davomat, -8 xarid |
| Xarid | `Purchase` | Do'kondan olingan mahsulot va uning holati |

**Eng muhim farq:** `Lesson` — reja ("nimani o'tamiz"), `GroupLesson` — fakt ("qachon, qaysi guruhda o'tdik"). Davomat faktga bog'lanadi, rejaga emas.

## 5. Arxitektura

Monolit Django 6 (MVT), SQLite (dev), server tomonda render qilinadigan templatelar. Tashqi frontend framework yo'q.

### App = kichik domen

Har app bitta savolga javob beradi va o'z modellarini o'zi boshqaradi:

| App | Javob beradigan savoli |
|---|---|
| `accounts` | Kim tizimda va qanday rolda? |
| `courses` | Nimani o'qitamiz va kim qaysi guruhda? |
| `schedule` | Qachon va qayerda dars bo'ladi / bo'ldi? |
| `attendance` | Darsga kim keldi? |
| `normativ` | O'quvchi mavzuni o'zlashtirdimi? |
| `coins` | Rag'bat qayerdan keldi va qayerga ketdi? |
| `news` | Markazda nima yangilik? |

Bog'liqlik yo'nalishi bir tomonlama: `accounts` hech kimga bog'lanmaydi, qolganlar unga tayanadi. `schedule`, `attendance`, `normativ` — `courses` ga tayanadi. Teskari import taqiqlanadi (aylanma bog'liqlik = dizayn xatosi).

### Qatlamlar

| Qatlam | Fayl | Mas'uliyati |
|---|---|---|
| Model | `models.py` | Domen tuzilishi va invariantlar (tayyor berildi) |
| Forma | `forms.py` | Kiritilgan ma'lumot validatsiyasi |
| View | `views.py` | Amaliyot stsenariysi: kim, nimani, qanday qiladi |
| Template | `templates/` | Faqat ko'rsatish. Biznes logika templatega kirmaydi |

## 6. Domen qoidalari (invariantlar)

Bular buzilmaydigan qonunlar. Har task shu qoidalarga bo'ysunadi:

1. **Coin balansi hech qayerda saqlanmaydi.** Balans = tranzaksiyalar yig'indisi. Ikkita raqam hech qachon "kelishmay" qolmaydi, chunki raqam bitta
2. **Har coin harakati — alohida `CoinTransaction` yozuvi.** Izohsiz, egasiz coin bo'lmaydi
3. **Coin idempotent beriladi** — bitta hodisa (bitta davomat, bitta normativ) uchun faqat bir marta. Qayta saqlash qayta coin bermaydi
4. **Moliyaviy tarix o'chmaydi.** Tranzaksiya va xarid `PROTECT` bilan himoyalangan; user o'chirilmaydi — `is_active=False` qilinadi
5. **O'quvchi guruhdan "o'chirilmaydi"** — `left_at` sanasi bilan chiqadi. A'zolik tarixi saqlanadi
6. **Bir xonada bir vaqtda bitta guruh.** Jadval saqlashdan oldin kesishuv tekshiriladi
7. **Davomat sanaga yoziladi, mavzuga emas** — avval `GroupLesson` yaratiladi, keyin davomat
8. **Normativ javobi bir marta topshiriladi** (baza darajasida unique). Baho `max_score` dan oshmaydi
9. **Guruhi bor kurs o'chmaydi** (`PROTECT`) — foydalanuvchiga tushunarli xabar ko'rsatiladi
10. **Holatni o'zgartiruvchi har qanday amal — faqat POST.** GET so'rov hech narsani o'zgartirmaydi

## 7. Model katalogi

Har model: nima uchun bor + asosiy qoidasi. To'liq field jadvallari `prezentatsiya.html` dagi ma'lumotnomada.

### accounts

- **`CustomUser`** — yagona kirish nuqtasi. `role` fieldi kim ekanini aytadi. Django'ning `AbstractUser` idan meros
- **`TeacherProfile`** — o'qituvchining kasbiy ma'lumotlari (mutaxassislik, bio). Userga OneToOne
- **`StudentProfile`** — o'quvchi ma'lumotlari + `coin_balance` property (6-bo'lim, 1-qoida)
- **`TimeStampedModel`** — abstract asos: har yozuvda `created_at` / `updated_at` avtomatik

### courses

- **`Course`** — o'quv dasturi. Aktiv/noaktiv bo'ladi, guruhi borligida o'chmaydi
- **`Module` / `Lesson`** — kurs ichki tuzilishi. `order` bilan tartiblanadi, (parent, order) juftligi unique
- **`Room`** — jismoniy xona. Jadval to'qnashuv tekshiruvining asosi
- **`Group`** — kurs + o'qituvchi + o'quvchilar. Mentor ixtiyoriy
- **`GroupStudent`** — a'zolik tarixi: `joined_at`, `left_at`, `is_active`. Oddiy M2M emasligi sababi — tarix (6-bo'lim, 5-qoida)

### schedule

- **`GroupSchedule`** — haftalik shablon (kun, vaqt, xona). Kelajak haqida gapiradi
- **`GroupLesson`** — bo'lib o'tgan dars (sana, mavzu, kim o'tdi). O'tmish haqida gapiradi. `teacher` bo'sh bo'lsa — guruh o'qituvchisi o'tgan

### attendance

- **`Attendance`** — (o'tilgan dars, o'quvchi) juftligiga bitta status. Saqlangach davomat coin'i yoziladi — faqat birinchi safar

### normativ

- **`Normativ`** — darsning savol to'plami
- **`NormativQuestion`** — savol + `max_score`
- **`NormativAnswer`** — javob hayot sikli: topshirildi (`score=null`) → tekshirildi (`score`, `feedback`, `checked_by`, `checked_at`). `is_checked` property shu holatni aytadi

### coins

- **`CoinTransaction`** — coin harakatining yagona manbasi. `amount` musbat yoki manfiy, `reason` — sabab
- **`ShopItem`** — do'kon mahsuloti (narx coin'da, stock)
- **`Purchase`** — xarid fakti + holati (kutilmoqda/berildi). O'z minus-tranzaksiyasiga OneToOne bog'langan — har xaridning pul izi bor

### news

- **`News`** — yangilik. `is_published=False` — qoralama, faqat muallif ko'radi

## 8. Ishlab chiqish qoidalari

1. Kod yozishdan oldin tegishli modelni oching va o'qing. Field nomini taxmin qilmang
2. Validatsiya — formada (`clean_*` / `clean`). View ichida if-else bilan tekshiruv yig'ilmasin
3. Signal ishlatmaymiz — coin yozish kabi biznes logika view ichida ochiq-oydin tursin
4. Ro'yxat sahifalarida query soni yozuvlar soniga bog'liq bo'lmasin (`select_related`, `prefetch_related`, `annotate`)
5. Saqlashdan keyin doim redirect (PRG) + `messages` bilan xabar
6. Har view kirishda ruxsat tekshiradi (`role_required`), teacher faqat o'z guruhlari ma'lumotini ko'radi
7. Task faqat kartadagi barcha qabul mezonlari bajarilganda yopiladi

## 9. Hujjatlar xaritasi

| Fayl | Nima uchun |
|---|---|
| `ARXITEKTURA.md` | Shu hujjat — nima va nima uchun qurayapmiz |
| `prezentatsiya.html` | 9 bosqich, 45 task kartasi + modellar ma'lumotnomasi |
| `figma_prompt.txt` | Dizayn generatori uchun brief (23 ekran) |
| `requirements.txt` | Loyiha bog'liqliklari |
