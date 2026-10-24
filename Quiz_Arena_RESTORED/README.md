# Quiz Arena PRO — Upgrade

Quiz Arena — o‘qituvchi/o‘quvchi hisoblari, testlar, reyting, sinflar, uy vazifalari, musiqa va Kahoot-uslubidagi jonli viktorina uchun Streamlit ilovasi.

## Windows / VS Code orqali ishga tushirish

1. ZIP arxivni chiqaring va `Quiz_Arena_RESTORED` papkasini VS Code’da oching.
2. Terminalda quyidagilarni birma-bir bajaring:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Brauzerda Streamlit bergan lokal manzil ochiladi (odatda `http://localhost:8501`).

## Internetga joylash (Streamlit Community Cloud)

1. GitHub’da yangi repository yarating.
2. Ushbu papkadagi `app.py`, `requirements.txt` va `README.md` fayllarini repository’ga yuklang.
3. Streamlit Community Cloud’da GitHub repository’ni ulang va `app.py` ni asosiy fayl sifatida tanlang.
4. Deploy tugagach, berilgan HTTPS havolani do‘stlaringizga ulashing.

**Muhim hosting eslatmasi:** hozirgi versiya SQLite’dan foydalanadi. Oddiy bulutli deploy’da lokal fayl saqlanishi doimiy bo‘lmasligi mumkin; bir nechta foydalanuvchi uchun barqaror umumiy ma’lumotlar bazasi kerak bo‘lsa, PostgreSQL kabi tashqi bazaga ko‘chirish tavsiya etiladi. Ommaviy xizmatga chiqarishdan oldin autentifikatsiya va xavfsizlikni ham kuchaytirish lozim. Jonli xona funksiyasi bir xil deploy qilingan ilovaga kirgan foydalanuvchilar uchun ishlaydi.

## AI test yordamchisi

- OpenAI API kaliti talab qilinadi. ChatGPT obunasi API kreditlarini avtomatik bermaydi.
- Kalitni AI test yordamchisi bo‘limiga kiriting yoki hosting secrets orqali sozlang.
- AI yaratgan savollarni ishlatishdan oldin tekshiring.

## Mavjud imkoniyatlar

- O‘qituvchi/o‘quvchi hisoblari
- Sinflar va sinf kodi
- Uy vazifalari va natijalar
- Taymerli quiz, ball, combo va tushuntirish
- XP, tangalar, darajalar, yutuqlar va TOP reyting
- Savol yaratish va tasdiqlash
- JSON/CSV import-eksport
- AI orqali test yaratish
- Audio fayl va YouTube musiqa bo‘limi
- Xona kodi, avtomatik yangilanish va jonli viktorina
- Mobil ekranlarga mos CSS va animatsiyali dizayn

## Ma’lumotlar bazasi

Ilova `quiz_arena_pro.db` faylidan foydalanadi. Yangilashdan oldin mavjud DB faylingizni zaxiralang.
