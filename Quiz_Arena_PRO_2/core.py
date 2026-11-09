"""Quiz Arena PRO — asosiy mantiq (ma’lumotlar bazasi, xavfsizlik, ball hisoblash, jonli xona).

Bu modul Streamlit’ga bog‘liq emas, shuning uchun uni alohida sinash mumkin.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import random
import secrets
import sqlite3
import time
from contextlib import contextmanager
from datetime import date, datetime, timedelta

DB_PATH = os.getenv("QUIZ_ARENA_DB_PATH", "quiz_arena_pro.db")

DIFFS = ["Oson", "O‘rta", "Qiyin"]
AVATARS = ["🦊", "🐼", "🐯", "🦁", "🐸", "🐵", "🦉", "🐙", "🦄", "🐲", "🚀", "⚡", "🎯", "👾", "🤖", "🧠"]

LEVEL_SIZE = 300
LEVEL_TITLES = ["Yangi boshlovchi", "Izlanuvchi", "Bilimdon", "Mohir", "Ustoz",
                "Ekspert", "Daho", "Afsona"]

# kalit: (belgi, nom, tavsif)
BADGES = {
    "xp100": ("💯", "Birinchi 100 XP", "100 XP to‘pladingiz"),
    "xp500": ("🏅", "500 XP klubi", "500 XP to‘pladingiz"),
    "xp1000": ("👑", "1000 XP afsonasi", "1000 XP to‘pladingiz"),
    "first_game": ("🎮", "Birinchi o‘yin", "Birinchi quizni yakunladingiz"),
    "games10": ("🔟", "Faol o‘yinchi", "10 ta quiz yakunladingiz"),
    "perfect": ("🎯", "Mukammal natija", "Kamida 5 savollik quizda 100% natija"),
    "combo5": ("🔥", "Combo ustasi", "Ketma-ket 5 ta to‘g‘ri javob"),
    "daily3": ("📅", "3 kunlik seriya", "Kunlik chaqiriqni 3 kun ketma-ket bajardingiz"),
    "daily7": ("🗓️", "Haftalik seriya", "Kunlik chaqiriqni 7 kun ketma-ket bajardingiz"),
    "homework": ("📚", "Intizomli o‘quvchi", "Birinchi uy vazifasini topshirdingiz"),
    "live_champion": ("🏆", "Jonli chempion", "Jonli viktorinada 1-o‘rinni oldingiz"),
    "helper": ("💡", "Hissa qo‘shuvchi", "Taklif qilgan savolingiz tasdiqlandi"),
}
LEGACY_BADGES = {"Birinchi 100 XP": "xp100", "500 XP klubi": "xp500"}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def today_str() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------- DB ulanish
@contextmanager
def conn():
    """Har amal uchun yangi ulanish: commit/rollback va albatta yopiladi."""
    con = sqlite3.connect(DB_PATH, timeout=15, check_same_thread=False)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def _add_col(c, table, col, ddl):
    cols = [r["name"] for r in c.execute(f"PRAGMA table_info({table})").fetchall()]
    if col not in cols:
        c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}")


SAMPLES = [
    ("Informatika", "Oson", "Kompyuterning tezkor xotirasi qaysi?", ["HDD", "RAM", "USB", "DVD"], "RAM", "RAM — ma’lumotlarni vaqtincha saqlaydigan tezkor xotira."),
    ("Informatika", "Oson", "1 bayt necha bitga teng?", ["4", "8", "16", "10"], "8", "1 bayt = 8 bit."),
    ("Informatika", "Oson", "Quyidagilardan qaysi biri kiritish qurilmasi?", ["Monitor", "Printer", "Klaviatura", "Karnay"], "Klaviatura", "Klaviatura kompyuterga ma’lumot kiritadi."),
    ("Python", "Oson", "Ekranga chiqarish funksiyasi qaysi?", ["input()", "print()", "len()", "type()"], "print()", "print() qiymatni ekranga chiqaradi."),
    ("Python", "O‘rta", "Python’da ro‘yxat qaysi qavs bilan yoziladi?", ["{}", "[]", "()", "<>"], "[]", "List kvadrat qavs bilan yoziladi."),
    ("Python", "Oson", "len('Salom') natijasi nechaga teng?", ["4", "5", "6", "7"], "5", "'Salom' so‘zida 5 ta belgi bor."),
    ("Python", "Oson", "Python’da izoh qaysi belgi bilan boshlanadi?", ["//", "#", "--", "/*"], "#", "Bir qatorli izoh # belgisi bilan yoziladi."),
    ("Python", "O‘rta", "range(3) qaysi sonlarni beradi?", ["1, 2, 3", "0, 1, 2", "0, 1, 2, 3", "1, 2"], "0, 1, 2", "range(3) 0 dan boshlab 3 gacha (3 kirmaydi) sonlarni beradi."),
    ("Matematika", "Oson", "12 × 8 nechiga teng?", ["86", "96", "88", "108"], "96", "12 × 8 = 96."),
    ("Matematika", "O‘rta", "144 ning kvadrat ildizi nechaga teng?", ["10", "11", "12", "14"], "12", "12 × 12 = 144."),
    ("Matematika", "O‘rta", "200 ning 15 foizi nechaga teng?", ["20", "25", "30", "35"], "30", "200 × 0,15 = 30."),
    ("Matematika", "Oson", "Uchburchak ichki burchaklari yig‘indisi necha gradus?", ["90°", "180°", "270°", "360°"], "180°", "Har qanday uchburchakda burchaklar yig‘indisi 180°."),
    ("Veb dasturlash", "O‘rta", "HTML asosan nima uchun ishlatiladi?", ["Sahifa tuzilishi", "Video montaj", "Audio yozish", "Antivirus"], "Sahifa tuzilishi", "HTML veb-sahifa tuzilishini belgilaydi."),
    ("Veb dasturlash", "Oson", "CSS nima uchun ishlatiladi?", ["Ma’lumotlar bazasi", "Sahifani bezash", "Server yozish", "Arxivlash"], "Sahifani bezash", "CSS sahifaning ko‘rinishini (rang, o‘lcham, joylashuv) boshqaradi."),
    ("Veb dasturlash", "O‘rta", "HTML’da eng katta sarlavha qaysi teg?", ["<h6>", "<head>", "<h1>", "<title>"], "<h1>", "<h1> — eng yuqori darajadagi sarlavha."),
    ("Ingliz tili", "Oson", "Apple so‘zining tarjimasi?", ["Nok", "Olma", "Uzum", "Shaftoli"], "Olma", "Apple — olma."),
    ("Ingliz tili", "Oson", "Book so‘zining tarjimasi?", ["Daftar", "Qalam", "Kitob", "Stol"], "Kitob", "Book — kitob."),
    ("Ingliz tili", "O‘rta", "'Go' fe’lining Past Simple shakli qaysi?", ["Goed", "Gone", "Went", "Going"], "Went", "Go — went — gone."),
    ("Geografiya", "Oson", "Dunyodagi eng katta okean qaysi?", ["Atlantika", "Hind", "Tinch", "Shimoliy Muz"], "Tinch", "Tinch okeani eng katta va eng chuqur okean."),
    ("Geografiya", "Oson", "O‘zbekiston poytaxti qaysi shahar?", ["Samarqand", "Toshkent", "Buxoro", "Namangan"], "Toshkent", "Toshkent — O‘zbekiston poytaxti."),
    ("Geografiya", "O‘rta", "Everest cho‘qqisi qaysi tog‘ tizmasida joylashgan?", ["Alp", "And", "Himolay", "Tyanshan"], "Himolay", "Everest (Jomolungma) Himolay tog‘larida."),
    ("Tarix", "O‘rta", "Amir Temur o‘z saltanatining poytaxtini qaysi shaharga qo‘ygan?", ["Buxoro", "Samarqand", "Xiva", "Termiz"], "Samarqand", "Amir Temur poytaxti — Samarqand."),
    ("Tarix", "Qiyin", "Mirzo Ulug‘bek rasadxonasi qaysi shaharda qurilgan?", ["Toshkent", "Buxoro", "Samarqand", "Qarshi"], "Samarqand", "Ulug‘bek rasadxonasi 1420-yillarda Samarqandda qurilgan."),
    ("Umumiy bilim", "Oson", "Quyosh tizimidagi eng katta sayyora qaysi?", ["Yer", "Mars", "Yupiter", "Saturn"], "Yupiter", "Yupiter — eng katta sayyora."),
    ("Umumiy bilim", "Oson", "Suvning kimyoviy formulasi qaysi?", ["CO₂", "H₂O", "O₂", "NaCl"], "H₂O", "Suv — ikki vodorod va bitta kislorod atomi."),
]


def init_db():
    with conn() as c:
        try:
            c.execute("PRAGMA journal_mode=WAL")
        except sqlite3.OperationalError:
            pass
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, name TEXT,
          role TEXT, xp INTEGER DEFAULT 0, coins INTEGER DEFAULT 0, created_at TEXT);
        CREATE TABLE IF NOT EXISTS questions(
          id INTEGER PRIMARY KEY, owner INTEGER, subject TEXT, difficulty TEXT,
          question TEXT, options TEXT, answer TEXT, explanation TEXT,
          approved INTEGER DEFAULT 1, created_at TEXT);
        CREATE TABLE IF NOT EXISTS classes(
          id INTEGER PRIMARY KEY, teacher INTEGER, name TEXT, code TEXT UNIQUE, created_at TEXT);
        CREATE TABLE IF NOT EXISTS members(class_id INTEGER, student INTEGER, joined_at TEXT,
          UNIQUE(class_id,student));
        CREATE TABLE IF NOT EXISTS assignments(
          id INTEGER PRIMARY KEY, class_id INTEGER, title TEXT, subject TEXT,
          questions TEXT, due TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS assignment_results(
          id INTEGER PRIMARY KEY, assignment_id INTEGER, student INTEGER,
          score INTEGER, correct INTEGER, total INTEGER, submitted_at TEXT,
          UNIQUE(assignment_id,student));
        CREATE TABLE IF NOT EXISTS results(
          id INTEGER PRIMARY KEY, user_id INTEGER, score INTEGER, correct INTEGER,
          total INTEGER, subject TEXT, played_at TEXT);
        CREATE TABLE IF NOT EXISTS achievements(
          user_id INTEGER, badge TEXT, earned_at TEXT, UNIQUE(user_id,badge));
        CREATE TABLE IF NOT EXISTS live_rooms(
          id INTEGER PRIMARY KEY, host_id INTEGER NOT NULL, code TEXT UNIQUE NOT NULL,
          title TEXT NOT NULL, questions TEXT NOT NULL, current_q INTEGER DEFAULT -1,
          status TEXT DEFAULT 'lobby', created_at TEXT);
        CREATE TABLE IF NOT EXISTS live_answers(
          id INTEGER PRIMARY KEY, room_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
          q_index INTEGER NOT NULL, answer TEXT, correct INTEGER DEFAULT 0, points INTEGER DEFAULT 0,
          answered_at TEXT, UNIQUE(room_id,user_id,q_index));
        CREATE TABLE IF NOT EXISTS live_players(
          room_id INTEGER NOT NULL, user_id INTEGER NOT NULL, joined_at TEXT,
          UNIQUE(room_id,user_id));
        CREATE TABLE IF NOT EXISTS question_stats(
          question_id INTEGER PRIMARY KEY, shown INTEGER DEFAULT 0, correct INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS daily_challenges(
          user_id INTEGER NOT NULL, day TEXT NOT NULL, score INTEGER, correct INTEGER, total INTEGER,
          UNIQUE(user_id,day));
        CREATE TABLE IF NOT EXISTS login_attempts(username TEXT, ts REAL);
        CREATE TABLE IF NOT EXISTS game_plays(
          id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, game TEXT NOT NULL, score INTEGER, perf REAL,
          xp INTEGER DEFAULT 0, coins INTEGER DEFAULT 0, day TEXT, played_at TEXT);
        CREATE INDEX IF NOT EXISTS idx_game_user ON game_plays(user_id,game);
        CREATE INDEX IF NOT EXISTS idx_results_user ON results(user_id);
        CREATE INDEX IF NOT EXISTS idx_live_answers_room ON live_answers(room_id,q_index);
        CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject);
        """)
        # Eski bazalarni yangilash (migratsiya)
        _add_col(c, "users", "avatar", "TEXT DEFAULT '🦊'")
        _add_col(c, "users", "theme", "TEXT DEFAULT 'neon'")
        _add_col(c, "users", "last_daily", "TEXT")
        _add_col(c, "users", "daily_streak", "INTEGER DEFAULT 0")
        _add_col(c, "results", "mode", "TEXT DEFAULT 'quiz'")
        _add_col(c, "assignment_results", "late", "INTEGER DEFAULT 0")
        _add_col(c, "live_rooms", "q_started", "REAL")
        _add_col(c, "live_rooms", "q_limit", "INTEGER DEFAULT 20")
        _add_col(c, "live_rooms", "phase", "TEXT DEFAULT 'question'")
        _add_col(c, "live_rooms", "awarded", "INTEGER DEFAULT 0")
        for old, new in LEGACY_BADGES.items():
            c.execute("UPDATE OR IGNORE achievements SET badge=? WHERE badge=?", (new, old))
        if c.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
            for s, d, q, o, a, e in SAMPLES:
                c.execute("""INSERT INTO questions(owner,subject,difficulty,question,options,answer,explanation,approved,created_at)
                          VALUES(NULL,?,?,?,?,?,?,1,?)""",
                          (s, d, q, json.dumps(o, ensure_ascii=False), a, e, now_iso()))


# ---------------------------------------------------------------- Xavfsizlik
def hash_password(password: str, iterations: int = 200_000) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), iterations).hex()
    return f"pbkdf2${iterations}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    if not stored:
        return False
    if stored.startswith("pbkdf2$"):
        try:
            _, it, salt, digest = stored.split("$")
            calc = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), int(it)).hex()
            return hmac.compare_digest(calc, digest)
        except (ValueError, TypeError):
            return False
    # eski (tuzsiz SHA-256) parollar — kirishda yangi formatga o‘tkaziladi
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored)


PUBLIC_COLS = "id,username,name,role,xp,coins,created_at,avatar,theme,last_daily,daily_streak"


def too_many_attempts(username: str, limit: int = 8, window: int = 300) -> bool:
    with conn() as c:
        n = c.execute("SELECT COUNT(*) FROM login_attempts WHERE username=? AND ts>?",
                      (username.lower(), time.time() - window)).fetchone()[0]
    return n >= limit


def authenticate(username: str, password: str):
    """To‘g‘ri bo‘lsa foydalanuvchi (parolsiz) qaytaradi, aks holda None."""
    username = username.strip()
    with conn() as c:
        row = c.execute("SELECT * FROM users WHERE username=? COLLATE NOCASE ORDER BY (username=?) DESC LIMIT 1",
                        (username, username)).fetchone()
        if row and verify_password(password, row["password"]):
            if not row["password"].startswith("pbkdf2$"):
                c.execute("UPDATE users SET password=? WHERE id=?", (hash_password(password), row["id"]))
            c.execute("DELETE FROM login_attempts WHERE username=?", (username.lower(),))
            return get_user_by_id(row["id"])
        c.execute("INSERT INTO login_attempts(username,ts) VALUES(?,?)", (username.lower(), time.time()))
        c.execute("DELETE FROM login_attempts WHERE ts<?", (time.time() - 3600,))
    return None


def create_user(username, password, name, role, avatar="🦊"):
    username = username.strip()
    with conn() as c:
        if c.execute("SELECT 1 FROM users WHERE username=? COLLATE NOCASE", (username,)).fetchone():
            raise ValueError("Bu login band.")
        c.execute("INSERT INTO users(username,password,name,role,created_at,avatar) VALUES(?,?,?,?,?,?)",
                  (username, hash_password(password), name.strip(), role, now_iso(), avatar))


def get_user_by_id(uid):
    with conn() as c:
        r = c.execute(f"SELECT {PUBLIC_COLS} FROM users WHERE id=?", (uid,)).fetchone()
    return dict(r) if r else None


def change_password(uid, old, new) -> bool:
    with conn() as c:
        row = c.execute("SELECT password FROM users WHERE id=?", (uid,)).fetchone()
        if not row or not verify_password(old, row["password"]):
            return False
        c.execute("UPDATE users SET password=? WHERE id=?", (hash_password(new), uid))
    return True


def update_profile(uid, name=None, avatar=None, theme=None):
    with conn() as c:
        if name:
            c.execute("UPDATE users SET name=? WHERE id=?", (name.strip(), uid))
        if avatar:
            c.execute("UPDATE users SET avatar=? WHERE id=?", (avatar, uid))
        if theme:
            c.execute("UPDATE users SET theme=? WHERE id=?", (theme, uid))


# ---------------------------------------------------------------- Daraja, XP, yutuqlar
def level_info(xp: int):
    lvl = xp // LEVEL_SIZE + 1
    title = LEVEL_TITLES[min(lvl - 1, len(LEVEL_TITLES) - 1)]
    return lvl, xp % LEVEL_SIZE, LEVEL_SIZE, title


def _grant(c, uid, key) -> bool:
    cur = c.execute("INSERT OR IGNORE INTO achievements(user_id,badge,earned_at) VALUES(?,?,?)", (uid, key, now_iso()))
    return cur.rowcount > 0


def grant_badge(uid, key) -> bool:
    with conn() as c:
        return _grant(c, uid, key)


def _award(c, uid, xp, coins):
    row = c.execute("SELECT xp FROM users WHERE id=?", (uid,)).fetchone()
    if not row:
        return {"level_up": False, "level": 1, "badges": []}
    old = row["xp"] or 0
    new = old + xp
    c.execute("UPDATE users SET xp=xp+?,coins=coins+? WHERE id=?", (xp, coins, uid))
    badges = [k for thr, k in ((100, "xp100"), (500, "xp500"), (1000, "xp1000")) if new >= thr and _grant(c, uid, k)]
    return {"level_up": new // LEVEL_SIZE > old // LEVEL_SIZE, "level": new // LEVEL_SIZE + 1, "badges": badges}


def award(uid, xp, coins, c=None):
    if c is not None:
        return _award(c, uid, xp, coins)
    with conn() as c2:
        return _award(c2, uid, xp, coins)


def spend(uid, coins) -> bool:
    with conn() as c:
        cur = c.execute("UPDATE users SET coins=coins-? WHERE id=? AND coins>=?", (coins, uid, coins))
        return cur.rowcount == 1


def earned_badges(uid) -> dict:
    with conn() as c:
        rows = c.execute("SELECT badge,earned_at FROM achievements WHERE user_id=?", (uid,)).fetchall()
    return {LEGACY_BADGES.get(r["badge"], r["badge"]): r["earned_at"] for r in rows}


# ---------------------------------------------------------------- Savollar
def normalize_difficulty(d) -> str:
    s = str(d or "").strip().lower().replace("’", "").replace("‘", "").replace("'", "")
    if s in ("oson", "easy", "легко", "easy "):
        return "Oson"
    if s in ("orta", "medium", "средне", "o rta"):
        return "O‘rta"
    if s in ("qiyin", "hard", "сложно"):
        return "Qiyin"
    return "Oson"


def get_questions(subject=None, difficulty=None, approved=True, search=None):
    """approved=True → faqat tasdiqlangan, False → faqat kutayotgan, None → hammasi."""
    sql, args = "SELECT * FROM questions WHERE 1=1", []
    if approved is True:
        sql += " AND approved=1"
    elif approved is False:
        sql += " AND approved=0"
    if subject:
        sql += " AND subject=?"
        args.append(subject)
    if difficulty:
        sql += " AND difficulty=?"
        args.append(difficulty)
    if search:
        sql += " AND question LIKE ?"
        args.append(f"%{search}%")
    with conn() as c:
        rows = c.execute(sql + " ORDER BY id DESC", args).fetchall()
    out = []
    for r in rows:
        q = dict(r)
        q["options"] = json.loads(q["options"])
        out.append(q)
    return out


def subjects():
    with conn() as c:
        return [r[0] for r in c.execute("SELECT DISTINCT subject FROM questions WHERE approved=1 AND subject IS NOT NULL ORDER BY subject")]


def question_exists(question, subject=None) -> bool:
    with conn() as c:
        return c.execute("SELECT 1 FROM questions WHERE lower(trim(question))=lower(trim(?)) LIMIT 1",
                         (question,)).fetchone() is not None


def add_question(owner, subject, difficulty, question, options, answer, explanation, approved=1):
    with conn() as c:
        c.execute("""INSERT INTO questions(owner,subject,difficulty,question,options,answer,explanation,approved,created_at)
                  VALUES(?,?,?,?,?,?,?,?,?)""",
                  (owner, subject, difficulty, question, json.dumps(options, ensure_ascii=False), answer,
                   explanation, approved, now_iso()))


def validate_question(question, options, answer):
    """None qaytarsa — hammasi joyida, aks holda xato matni."""
    options = [str(o).strip() for o in options]
    if not str(question).strip():
        return "Savol matni bo‘sh."
    if len(options) != 4 or any(not o for o in options):
        return "Aynan 4 ta to‘ldirilgan variant kerak."
    if len({o.lower() for o in options}) != 4:
        return "Variantlar bir-biridan farq qilishi kerak."
    if answer not in options:
        return "To‘g‘ri javob variantlar orasida bo‘lishi kerak."
    return None


def normalize_question(raw: dict):
    """Import qilinadigan qatorni tozalaydi. (savol_dict, None) yoki (None, sabab)."""
    q = str(raw.get("question") or raw.get("text") or "").strip()
    opts = raw.get("options", [])
    if isinstance(opts, str):
        s = opts.strip()
        if s.startswith("["):
            try:
                opts = json.loads(s)
            except ValueError:
                opts = s.split("|")
        else:
            opts = s.split("|")
    opts = [str(o).strip() for o in (opts or [])]
    ans = str(raw.get("answer", "")).strip()
    if ans not in opts and len(ans) == 1 and ans.upper() in "ABCD" and len(opts) == 4:
        ans = opts["ABCD".index(ans.upper())]
    err = validate_question(q, opts, ans)
    if err:
        return None, err
    return {"subject": str(raw.get("subject") or raw.get("category") or "Umumiy").strip() or "Umumiy",
            "difficulty": normalize_difficulty(raw.get("difficulty")),
            "question": q, "options": opts, "answer": ans,
            "explanation": str(raw.get("explanation") or "").strip()}, None


def record_stat(c, qid, ok):
    if not qid:
        return
    c.execute("INSERT OR IGNORE INTO question_stats(question_id,shown,correct) VALUES(?,0,0)", (qid,))
    c.execute("UPDATE question_stats SET shown=shown+1, correct=correct+? WHERE question_id=?", (1 if ok else 0, qid))


def hardest_questions(limit=5, min_shown=3):
    with conn() as c:
        rows = c.execute("""SELECT q.id,q.question,q.subject,s.shown,s.correct,
                  ROUND(100.0*s.correct/s.shown) AS pct
                  FROM question_stats s JOIN questions q ON q.id=s.question_id
                  WHERE s.shown>=? ORDER BY (1.0*s.correct/s.shown) ASC, s.shown DESC LIMIT ?""",
                         (min_shown, limit)).fetchall()
    return [dict(r) for r in rows]


def delete_questions(ids):
    with conn() as c:
        for i in ids:
            c.execute("DELETE FROM questions WHERE id=?", (int(i),))
            c.execute("DELETE FROM question_stats WHERE question_id=?", (int(i),))


def approve_question(qid):
    with conn() as c:
        row = c.execute("SELECT owner,approved FROM questions WHERE id=?", (qid,)).fetchone()
        if not row:
            return
        c.execute("UPDATE questions SET approved=1 WHERE id=?", (qid,))
        if row["owner"] and not row["approved"]:
            owner_role = c.execute("SELECT role FROM users WHERE id=?", (row["owner"],)).fetchone()
            if owner_role and owner_role["role"] == "student":
                _award(c, row["owner"], 30, 10)
                _grant(c, row["owner"], "helper")


# ---------------------------------------------------------------- Natijalar va kunlik chaqiriq
def complete_quiz(uid, subject, score, correct, total, best_streak):
    xp, coins = correct * 50, correct * 10
    perfect = total >= 5 and correct == total
    if perfect:
        xp, coins = xp + 100, coins + 25
    with conn() as c:
        c.execute("INSERT INTO results(user_id,score,correct,total,subject,played_at,mode) VALUES(?,?,?,?,?,?,?)",
                  (uid, score, correct, total, subject, datetime.now().strftime("%Y-%m-%d %H:%M"), "quiz"))
        info = _award(c, uid, xp, coins)
        n = c.execute("SELECT COUNT(*) FROM results WHERE user_id=?", (uid,)).fetchone()[0]
        for cond, key in ((n >= 1, "first_game"), (n >= 10, "games10"), (perfect, "perfect"), (best_streak >= 5, "combo5")):
            if cond and _grant(c, uid, key):
                info["badges"].append(key)
    info.update(xp=xp, coins=coins)
    return info


def daily_questions(day=None, n=5):
    day = day or today_str()
    pool = sorted(get_questions(), key=lambda q: q["id"])
    return random.Random(day).sample(pool, min(n, len(pool)))


def daily_status(user):
    """(bugun_bajarilganmi, joriy_seriya)"""
    with conn() as c:
        done = c.execute("SELECT * FROM daily_challenges WHERE user_id=? AND day=?", (user["id"], today_str())).fetchone()
    last = user.get("last_daily")
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    streak = user.get("daily_streak") or 0
    if last not in (today_str(), yesterday):
        streak = 0
    return (dict(done) if done else None), streak


def complete_daily(uid, score, correct, total, best_streak):
    """Bugun birinchi marta bajarilsa mukofot ma’lumotini, aks holda None qaytaradi."""
    with conn() as c:
        cur = c.execute("INSERT OR IGNORE INTO daily_challenges(user_id,day,score,correct,total) VALUES(?,?,?,?,?)",
                        (uid, today_str(), score, correct, total))
        if cur.rowcount == 0:
            return None
        row = c.execute("SELECT last_daily,daily_streak FROM users WHERE id=?", (uid,)).fetchone()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        streak = (row["daily_streak"] or 0) + 1 if row["last_daily"] == yesterday else 1
        c.execute("UPDATE users SET last_daily=?,daily_streak=? WHERE id=?", (today_str(), streak, uid))
        xp, coins = correct * 40 + 30, 5 + min(streak, 7) * 3
        info = _award(c, uid, xp, coins)
        c.execute("INSERT INTO results(user_id,score,correct,total,subject,played_at,mode) VALUES(?,?,?,?,?,?,?)",
                  (uid, score, correct, total, "Kunlik chaqiriq", datetime.now().strftime("%Y-%m-%d %H:%M"), "daily"))
        for cond, key in ((streak >= 3, "daily3"), (streak >= 7, "daily7"), (best_streak >= 5, "combo5")):
            if cond and _grant(c, uid, key):
                info["badges"].append(key)
    info.update(xp=xp, coins=coins, streak=streak)
    return info


def recent_results(uid, n=15):
    with conn() as c:
        rows = c.execute("SELECT * FROM results WHERE user_id=? ORDER BY id DESC LIMIT ?", (uid, n)).fetchall()
    return [dict(r) for r in reversed(rows)]


def subject_stats(uid):
    with conn() as c:
        rows = c.execute("""SELECT subject,SUM(correct) c,SUM(total) t FROM results
                         WHERE user_id=? GROUP BY subject ORDER BY t DESC""", (uid,)).fetchall()
    return [dict(r) for r in rows if r["t"]]


# ---------------------------------------------------------------- Reyting
def top_xp(limit=20):
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT id,name,avatar,role,xp,coins FROM users ORDER BY xp DESC,coins DESC,id LIMIT ?", (limit,))]


def weekly_board(limit=20):
    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
    with conn() as c:
        return [dict(r) for r in c.execute("""SELECT u.name,u.avatar,SUM(r.score) pts,COUNT(*) games
              FROM results r JOIN users u ON u.id=r.user_id WHERE r.played_at>=?
              GROUP BY u.id ORDER BY pts DESC LIMIT ?""", (cutoff, limit))]


def best_games(limit=20):
    with conn() as c:
        return [dict(r) for r in c.execute("""SELECT u.name,u.avatar,r.score,r.correct,r.total,r.subject,r.played_at
              FROM results r JOIN users u ON u.id=r.user_id ORDER BY r.score DESC LIMIT ?""", (limit,))]


def user_rank(uid) -> int:
    with conn() as c:
        return c.execute("SELECT COUNT(*)+1 FROM users WHERE xp>(SELECT xp FROM users WHERE id=?)", (uid,)).fetchone()[0]


# ---------------------------------------------------------------- Sinflar va uy vazifalari
def new_code():
    return "".join(random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(6))


def create_class(teacher_id, name):
    for _ in range(10):
        code = new_code()
        try:
            with conn() as c:
                c.execute("INSERT INTO classes(teacher,name,code,created_at) VALUES(?,?,?,?)", (teacher_id, name, code, now_iso()))
            return code
        except sqlite3.IntegrityError:
            continue
    raise RuntimeError("Kod yaratib bo‘lmadi")


def join_class(student_id, code):
    """('ok'|'again'|'none', sinf_nomi)"""
    with conn() as c:
        cl = c.execute("SELECT * FROM classes WHERE code=?", (code.strip().upper(),)).fetchone()
        if not cl:
            return "none", None
        cur = c.execute("INSERT OR IGNORE INTO members(class_id,student,joined_at) VALUES(?,?,?)", (cl["id"], student_id, now_iso()))
        return ("ok" if cur.rowcount else "again"), cl["name"]


def delete_class(class_id, teacher_id):
    with conn() as c:
        if not c.execute("SELECT 1 FROM classes WHERE id=? AND teacher=?", (class_id, teacher_id)).fetchone():
            return
        ids = [r[0] for r in c.execute("SELECT id FROM assignments WHERE class_id=?", (class_id,))]
        for i in ids:
            c.execute("DELETE FROM assignment_results WHERE assignment_id=?", (i,))
        c.execute("DELETE FROM assignments WHERE class_id=?", (class_id,))
        c.execute("DELETE FROM members WHERE class_id=?", (class_id,))
        c.execute("DELETE FROM classes WHERE id=?", (class_id,))


def delete_assignment(assignment_id):
    with conn() as c:
        c.execute("DELETE FROM assignment_results WHERE assignment_id=?", (assignment_id,))
        c.execute("DELETE FROM assignments WHERE id=?", (assignment_id,))


def create_assignment(class_id, title, subject, qs, due):
    with conn() as c:
        c.execute("INSERT INTO assignments(class_id,title,subject,questions,due,created_at) VALUES(?,?,?,?,?,?)",
                  (class_id, title, subject, json.dumps(qs, ensure_ascii=False), str(due), now_iso()))


def submit_assignment(assignment_id, uid, marks):
    """marks = [(savol_id, to‘g‘rimi), ...]. Birinchi topshirishda ma’lumot qaytaradi; qayta topshirishda None."""
    correct, total = sum(1 for _, ok in marks if ok), len(marks)
    with conn() as c:
        a = c.execute("SELECT due FROM assignments WHERE id=?", (assignment_id,)).fetchone()
        late = 1 if (a and a["due"] and today_str() > a["due"]) else 0
        cur = c.execute("""INSERT OR IGNORE INTO assignment_results(assignment_id,student,score,correct,total,submitted_at,late)
                        VALUES(?,?,?,?,?,?,?)""", (assignment_id, uid, correct * 100, correct, total, now_iso(), late))
        if cur.rowcount == 0:
            return None
        xp = correct * 50
        if late:
            xp //= 2
        info = _award(c, uid, xp, correct * 10)
        if _grant(c, uid, "homework"):
            info["badges"].append("homework")
        for qid, ok in marks:
            record_stat(c, qid, ok)
        info.update(xp=xp, late=bool(late))
        return info


# ---------------------------------------------------------------- Jonli viktorina
def live_points(ok: bool, elapsed: float, limit: float, streak: int) -> int:
    """Kahoot uslubi: tezroq javob — ko‘proq ball (500–1000) + seriya bonusi (maks. +250)."""
    if not ok:
        return 0
    frac = min(max(elapsed / max(limit, 1), 0.0), 1.0)
    return round(1000 * (1 - frac / 2)) + min(streak, 5) * 50


def create_room(host_id, title, qs, limit):
    for _ in range(10):
        code = new_code()
        try:
            with conn() as c:
                c.execute("""INSERT INTO live_rooms(host_id,code,title,questions,current_q,status,created_at,q_limit,phase)
                          VALUES(?,?,?,?,?,?,?,?,?)""",
                          (host_id, code, title, json.dumps(qs, ensure_ascii=False), -1, "lobby", now_iso(), limit, "question"))
            return code
        except sqlite3.IntegrityError:
            continue
    raise RuntimeError("Kod yaratib bo‘lmadi")


def get_room(room_id):
    with conn() as c:
        r = c.execute("SELECT * FROM live_rooms WHERE id=?", (room_id,)).fetchone()
    return dict(r) if r else None


def host_rooms(host_id, limit=10):
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM live_rooms WHERE host_id=? ORDER BY id DESC LIMIT ?", (host_id, limit))]


def join_room(code, uid):
    """('ok', room) | ('none', None) | ('finished', room)"""
    with conn() as c:
        r = c.execute("SELECT * FROM live_rooms WHERE code=?", (code.strip().upper(),)).fetchone()
        if not r:
            return "none", None
        if r["status"] == "finished":
            return "finished", dict(r)
        c.execute("INSERT OR IGNORE INTO live_players(room_id,user_id,joined_at) VALUES(?,?,?)", (r["id"], uid, now_iso()))
        return "ok", dict(r)


def start_room(room_id, host_id):
    with conn() as c:
        c.execute("""UPDATE live_rooms SET status='live',current_q=0,q_started=?,phase='question'
                  WHERE id=? AND host_id=? AND status='lobby'""", (time.time(), room_id, host_id))


def set_phase(room_id, phase):
    with conn() as c:
        c.execute("UPDATE live_rooms SET phase=? WHERE id=?", (phase, room_id))


def advance_room(room_id, host_id):
    last = False
    with conn() as c:
        r = c.execute("SELECT * FROM live_rooms WHERE id=? AND host_id=?", (room_id, host_id)).fetchone()
        if not r or r["status"] != "live":
            return
        ni = r["current_q"] + 1
        if ni >= len(json.loads(r["questions"])):
            last = True
        else:
            c.execute("UPDATE live_rooms SET current_q=?,q_started=?,phase='question' WHERE id=?", (ni, time.time(), room_id))
    if last:
        finish_room(room_id, host_id)


def _scoreboard(c, room_id):
    rows = c.execute("""SELECT u.id user_id,u.name,u.avatar,COALESCE(SUM(a.points),0) points,
                COALESCE(SUM(a.correct),0) correct_count
                FROM live_players p JOIN users u ON u.id=p.user_id
                LEFT JOIN live_answers a ON a.room_id=p.room_id AND a.user_id=p.user_id
                WHERE p.room_id=? GROUP BY u.id ORDER BY points DESC,u.name""", (room_id,)).fetchall()
    return [dict(r) for r in rows]


def room_scoreboard(room_id):
    with conn() as c:
        return _scoreboard(c, room_id)


def finish_room(room_id, host_id):
    with conn() as c:
        cur = c.execute("UPDATE live_rooms SET status='finished',phase='reveal',awarded=1 WHERE id=? AND host_id=? AND status!='finished'",
                        (room_id, host_id))
        if cur.rowcount == 0:
            return
        board = [p for p in _scoreboard(c, room_id) if p["points"] > 0]
        for place, (xp, coins) in enumerate([(100, 30), (60, 20), (30, 10)]):
            if place < len(board):
                _award(c, board[place]["user_id"], xp, coins)
        if len(_scoreboard(c, room_id)) >= 2 and board:
            _grant(c, board[0]["user_id"], "live_champion")


def delete_room(room_id, host_id):
    with conn() as c:
        if c.execute("SELECT 1 FROM live_rooms WHERE id=? AND host_id=?", (room_id, host_id)).fetchone():
            c.execute("DELETE FROM live_answers WHERE room_id=?", (room_id,))
            c.execute("DELETE FROM live_players WHERE room_id=?", (room_id,))
            c.execute("DELETE FROM live_rooms WHERE id=?", (room_id,))


def effective_phase(room) -> str:
    if room["status"] != "live":
        return room["status"]
    if room["phase"] == "reveal":
        return "reveal"
    if room["q_started"] and time.time() >= room["q_started"] + (room["q_limit"] or 20):
        return "reveal"
    return "question"


def time_left(room) -> float:
    if not room.get("q_started"):
        return float(room.get("q_limit") or 20)
    return max(0.0, room["q_started"] + (room["q_limit"] or 20) - time.time())


def answer_count(room_id, qi):
    with conn() as c:
        a = c.execute("SELECT COUNT(*) FROM live_answers WHERE room_id=? AND q_index=?", (room_id, qi)).fetchone()[0]
        p = c.execute("SELECT COUNT(*) FROM live_players WHERE room_id=?", (room_id,)).fetchone()[0]
    return a, p


def answer_distribution(room_id, qi):
    with conn() as c:
        return {r["answer"]: r["n"] for r in c.execute(
            "SELECT answer,COUNT(*) n FROM live_answers WHERE room_id=? AND q_index=? GROUP BY answer", (room_id, qi))}


def my_live_answer(room_id, uid, qi):
    with conn() as c:
        r = c.execute("SELECT * FROM live_answers WHERE room_id=? AND user_id=? AND q_index=?", (room_id, uid, qi)).fetchone()
    return dict(r) if r else None


def live_streak(c, room_id, uid, qi) -> int:
    rows = c.execute("SELECT q_index,correct FROM live_answers WHERE room_id=? AND user_id=? AND q_index<? ORDER BY q_index DESC",
                     (room_id, uid, qi)).fetchall()
    streak, expected = 0, qi - 1
    for r in rows:
        if r["q_index"] == expected and r["correct"]:
            streak += 1
            expected -= 1
        else:
            break
    return streak


def submit_live_answer(room_id, uid, option):
    """{'error': 'closed'|'late'|'dup'} yoki {'points','correct','streak','level_up',...}"""
    with conn() as c:
        room = c.execute("SELECT * FROM live_rooms WHERE id=?", (room_id,)).fetchone()
        if not room or room["status"] != "live" or room["phase"] != "question":
            return {"error": "closed"}
        qi = room["current_q"]
        q = json.loads(room["questions"])[qi]
        limit = room["q_limit"] or 20
        elapsed = time.time() - (room["q_started"] or time.time())
        if elapsed > limit + 1.5:
            return {"error": "late"}
        ok = option == q["answer"]
        streak = live_streak(c, room_id, uid, qi)
        pts = live_points(ok, elapsed, limit, streak)
        c.execute("INSERT OR IGNORE INTO live_players(room_id,user_id,joined_at) VALUES(?,?,?)", (room_id, uid, now_iso()))
        cur = c.execute("""INSERT OR IGNORE INTO live_answers(room_id,user_id,q_index,answer,correct,points,answered_at)
                        VALUES(?,?,?,?,?,?,?)""", (room_id, uid, qi, option, int(ok), pts, now_iso()))
        if cur.rowcount == 0:
            return {"error": "dup"}
        record_stat(c, q.get("id"), ok)
        info = _award(c, uid, min(10, max(2, pts // 100)), 2) if ok else {"level_up": False, "level": 1, "badges": []}
        a = c.execute("SELECT COUNT(*) FROM live_answers WHERE room_id=? AND q_index=?", (room_id, qi)).fetchone()[0]
        p = c.execute("SELECT COUNT(*) FROM live_players WHERE room_id=?", (room_id,)).fetchone()[0]
        if a >= p:  # hamma javob berdi — natija darhol ko‘rsatiladi
            c.execute("UPDATE live_rooms SET phase='reveal' WHERE id=?", (room_id,))
    info.update(points=pts, correct=ok, streak=streak + 1 if ok else 0)
    return info


# ---------------------------------------------------------------- Savollar bankini tahrirlash
def update_question(qid, subject, difficulty, question):
    with conn() as c:
        c.execute("UPDATE questions SET subject=?,difficulty=?,question=? WHERE id=?",
                  (subject.strip(), difficulty, question.strip(), int(qid)))


def set_unapproved(qid):
    with conn() as c:
        c.execute("UPDATE questions SET approved=0 WHERE id=?", (int(qid),))


def my_suggestions(uid):
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT id,subject,difficulty,question,approved FROM questions WHERE owner=? ORDER BY id DESC LIMIT 30", (uid,))]


# ---------------------------------------------------------------- Mini-o‘yinlar
GAME_XP_CAP = 300  # kuniga mini-o‘yinlardan olinadigan maksimal XP

BADGES.update({
    "gamer5": ("🕹️", "O‘yinchi", "5 xil mini-o‘yinni sinab ko‘rdingiz"),
    "gamer15": ("🎰", "Arkada ustasi", "15 xil mini-o‘yinni sinab ko‘rdingiz"),
    "gamer30": ("🌟", "Barcha o‘yinlar", "30 xil mini-o‘yinni sinab ko‘rdingiz"),
})


def game_xp_today(uid) -> int:
    with conn() as c:
        return c.execute("SELECT COALESCE(SUM(xp),0) FROM game_plays WHERE user_id=? AND day=?", (uid, today_str())).fetchone()[0]


def complete_game(uid, game, score, perf):
    """perf 0..1 — natija sifati. Kunlik XP limiti bor. Ma’lumot qaytaradi."""
    perf = min(max(float(perf), 0.0), 1.0)
    with conn() as c:
        used = c.execute("SELECT COALESCE(SUM(xp),0) FROM game_plays WHERE user_id=? AND day=?", (uid, today_str())).fetchone()[0]
        xp = min(round(10 + 40 * perf), max(0, GAME_XP_CAP - used))
        coins = round(2 + 8 * perf) if xp > 0 else 0
        prev = c.execute("SELECT MAX(score) FROM game_plays WHERE user_id=? AND game=?", (uid, game)).fetchone()[0]
        c.execute("INSERT INTO game_plays(user_id,game,score,perf,xp,coins,day,played_at) VALUES(?,?,?,?,?,?,?,?)",
                  (uid, game, score, perf, xp, coins, today_str(), now_iso()))
        info = _award(c, uid, xp, coins)
        kinds = c.execute("SELECT COUNT(DISTINCT game) FROM game_plays WHERE user_id=?", (uid,)).fetchone()[0]
        for n, key in ((5, "gamer5"), (15, "gamer15"), (30, "gamer30")):
            if kinds >= n and _grant(c, uid, key):
                info["badges"].append(key)
    info.update(xp=xp, coins=coins, capped=(xp == 0), new_best=(prev is None or score > prev))
    return info


def game_best(uid) -> dict:
    with conn() as c:
        return {r["game"]: r["m"] for r in c.execute(
            "SELECT game,MAX(score) m FROM game_plays WHERE user_id=? GROUP BY game", (uid,))}


def game_top(game, limit=5):
    with conn() as c:
        return [dict(r) for r in c.execute("""SELECT u.name,u.avatar,MAX(g.score) score,COUNT(*) plays
              FROM game_plays g JOIN users u ON u.id=g.user_id WHERE g.game=?
              GROUP BY u.id ORDER BY score DESC LIMIT ?""", (game, limit))]
