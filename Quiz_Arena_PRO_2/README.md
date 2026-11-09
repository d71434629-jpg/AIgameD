# Quiz Arena PRO 2.0

O‘qituvchi/o‘quvchi hisoblari, testlar, sinflar, uy vazifalari, kunlik chaqiriq, Kahoot-uslubidagi jonli viktorina, AI test yordamchisi va yutuqlar tizimi bilan Streamlit ilovasi.

## Fayllar

| Fayl | Vazifasi |
|---|---|
| `app.py` | Interfeys (sahifalar, dizayn) |
| `core.py` | Ma’lumotlar bazasi, xavfsizlik, ball hisoblash, jonli xona mantiqi |
| `games.py` | 30 ta mini-o‘yin va «O‘yinlar markazi» |
| `requirements.txt` | Kutubxonalar |
| `.streamlit/config.toml` | Qorong‘i mavzu va asosiy ranglar |

Hosting’ga yuklashda **barcha fayllar** (shu jumladan `core.py`, `games.py` va `.streamlit` papkasi) repository’da bo‘lishi kerak.

## Windows / VS Code orqali ishga tushirish

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Brauzerda odatda `http://localhost:8501` ochiladi.

## Eski versiyadan o‘tish

Eski `quiz_arena_pro.db` faylini yangi papkaga qo‘ying (avval nusxasini zaxiralang). Ilova bazani o‘zi yangilaydi: foydalanuvchilar, savollar, sinflar, natijalar va yutuqlar saqlanadi, eski parollar birinchi kirishda xavfsiz formatga o‘tkaziladi.

## 🕹️ O‘yinlar markazi — 30 ta mini-o‘yin

| Bo‘lim | O‘yinlar |
|---|---|
| 🧠 Bilim (savollar bankidan) | Blitz 60 · Omon qolish · To‘g‘ri/Noto‘g‘ri · Bot bilan duel · Xavf-xatar · Million zinapoyasi · Yozib javob ber · Qiyinlashib boradi · Chaqmoq raundi · Omad g‘ildiragi · Moslashtirish · Takrorlash kartalari |
| 🌍 Dunyo | Poytaxtni top · Qit’ani top · Emoji topishmoq · Qaysi kattaroq? |
| 🔢 Raqamlar | Matematika blitz · Sonlar ketma-ketligi · Sonni top · Raqamlar xotirasi · Sonlarni tartiblash · Kod buzar |
| 🔤 So‘zlar | So‘z topish (Wordle) · Osilgan odam · So‘z aralashmasi |
| 🧩 Mantiq | Xotira kartalari · Krestik-nolik · Ranglar tuzog‘i · Mina qidiruvchi |
| 😎 Dam olish | Ilon (XP yo‘q) |

- Har o‘yin tugagach XP va tanga beriladi (natija sifatiga qarab). Kuniga mini-o‘yinlardan **maksimal 300 XP** olinadi.
- Har o‘yin bo‘yicha shaxsiy rekord va umumiy rekordlar jadvali bor.
- 5, 15 va 30 xil o‘yin sinab ko‘rgan uchun maxsus yutuqlar.
- Savollar bankiga asoslangan o‘yinlar savol qo‘shilgani sari boyib boradi (kamida 4–5 ta savol bo‘lsin).

## Yangi imkoniyatlar

**O‘yin va rag‘bat**
- 🔥 Kunlik chaqiriq: hamma uchun bir xil 5 savol, kunlik seriya va seriya bonusi
- 🌓 Yordamchilar: 50/50 va +10 soniya (tangalar evaziga)
- 🛠️ «Xatolarni qayta ishlash» mashq rejimi
- 12 ta yutuq, daraja nomlari (Yangi boshlovchi → Afsona), avatarlar
- 5 ta dizayn mavzusi (Neon, Pixel-art, Tabiat, Quyosh botishi, Minimalist) — profilda saqlanadi

**Jonli viktorina (Kahoot uslubi)**
- Kutish zali: o‘yinchilar boshlanishdan oldin ko‘rinadi
- Har savolga taymer; tezroq javob — ko‘proq ball (500–1000) + seriya bonusi
- Hamma javob bersa yoki vaqt tugasa natija avtomatik ochiladi
- Javoblar taqsimoti grafigi, jonli TOP-5, yakunda podium va bonuslar (1-o‘rin +100 XP)
- Natijalarni CSV qilib yuklab olish

**O‘qituvchi uchun**
- Eng qiyin savollar statistikasi
- Vazifalar: muddat, kechikish belgisi, topshirmaganlar ro‘yxati, o‘rtacha natija, CSV
- Savollar bankini jadvalda tahrirlash, qidirish, filtrlash, ommaviy tasdiqlash
- Import: oldindan ko‘rish, takroriy va xato qatorlarni ajratish, namuna fayl
- AI savollarini tanlab saqlash

**Reyting va profil**
- XP, haftalik ball va eng yaxshi o‘yinlar bo‘yicha reyting, podium
- Statistika grafiklari (aniqlik dinamikasi, fanlar bo‘yicha natija)
- Pomodoro fokus taymeri

## Xavfsizlik

- Parollar PBKDF2-SHA256 bilan tuzlangan holda saqlanadi
- Bir loginga ketma-ket noto‘g‘ri urinishlar vaqtincha bloklanadi
- Foydalanuvchi matnlari sahifada HTML sifatida emas, xavfsiz ko‘rsatiladi
- **O‘qituvchi kodi:** `QUIZ_ARENA_TEACHER_CODE` o‘rnatilsa, o‘qituvchi sifatida ro‘yxatdan o‘tish shu kodni talab qiladi. Ommaviy sayt uchun buni albatta sozlang, aks holda istalgan kishi o‘zini o‘qituvchi deb ro‘yxatdan o‘tkaza oladi.

## Sozlamalar (muhit o‘zgaruvchilari yoki Streamlit Secrets)

| Nomi | Ma’nosi |
|---|---|
| `QUIZ_ARENA_DB_PATH` | Baza fayli manzili (standart: `quiz_arena_pro.db`) |
| `QUIZ_ARENA_TEACHER_CODE` | O‘qituvchi ro‘yxatdan o‘tish kodi |
| `OPENAI_API_KEY` | AI test yordamchisi uchun kalit |
| `OPENAI_MODEL` | AI modeli (standart: `gpt-4o-mini`) |

Streamlit Community Cloud’da: **App settings → Secrets** bo‘limiga yozing:

```toml
QUIZ_ARENA_TEACHER_CODE = "o‘zingiz-o‘ylab-topgan-kod"
OPENAI_API_KEY = "sk-..."
```

## Internetga joylash (Streamlit Community Cloud)

1. GitHub’da repository yarating va yuqoridagi fayllarni yuklang.
2. Streamlit Community Cloud’da repository’ni ulang, asosiy fayl: `app.py`.
3. Secrets’ni sozlang va deploy qiling.

**Muhim:** hozirgi versiya SQLite’dan foydalanadi. Community Cloud’da lokal fayl tizimi doimiy emas — ilova qayta ishga tushganda ma’lumotlar yo‘qolishi mumkin. Doimiy ishlatish uchun VPS/server (bazani saqlab turuvchi disk bilan) yoki PostgreSQL kabi tashqi bazaga ko‘chirish kerak. Jonli viktorina bir xil deploy qilingan ilovaga kirgan foydalanuvchilar uchun ishlaydi.

## Eslatmalar

- AI yaratgan savollarni darsda ishlatishdan oldin albatta tekshiring.
- Jonli viktorinada ball serverdagi vaqt bo‘yicha hisoblanadi; sahifa har ~2 soniyada yangilanadi, shuning uchun u millisekundli aniq reyting emas.
