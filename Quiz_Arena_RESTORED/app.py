import streamlit as st
from streamlit_autorefresh import st_autorefresh
import sqlite3, hashlib, json, random, csv, io, time, secrets, os
from datetime import datetime, date

DB = "quiz_arena_pro.db"
st.set_page_config(page_title="Quiz Arena PRO", page_icon="🎮", layout="wide", initial_sidebar_state="expanded")

# ---------- Database ----------
def db():
    con = sqlite3.connect(DB, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def hpass(p):
    return hashlib.sha256(p.encode("utf-8")).hexdigest()

def init_db():
    with db() as c:
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
        """)
        if c.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
            samples = [
              ("Informatika","Oson","Kompyuterning tezkor xotirasi qaysi?",["HDD","RAM","USB","DVD"],"RAM","RAM — ma’lumotlarni vaqtincha saqlaydigan tezkor xotira."),
              ("Python","Oson","Ekranga chiqarish funksiyasi qaysi?",["input()","print()","len()","type()"],"print()","print() qiymatni ekranga chiqaradi."),
              ("Matematika","Oson","12 × 8 nechiga teng?",["86","96","88","108"],"96","12 × 8 = 96."),
              ("Veb dasturlash","O‘rta","HTML asosan nima uchun ishlatiladi?",["Sahifa tuzilishi","Video montaj","Audio yozish","Antivirus"],"Sahifa tuzilishi","HTML veb-sahifa tuzilishini belgilaydi."),
              ("Ingliz tili","Oson","Apple so‘zining tarjimasi?",["Nok","Olma","Uzum","Shaftoli"],"Olma","Apple — olma."),
              ("Python","O‘rta","Python’da ro‘yxat qaysi qavs bilan yoziladi?",["{}","[]","()","<>"],"[]","List kvadrat qavs bilan yoziladi."),
              ("Matematika","O‘rta","144 ning kvadrat ildizi nechaga teng?",["10","11","12","14"],"12","12 × 12 = 144.")
            ]
            for s,d,q,o,a,e in samples:
                c.execute("INSERT INTO questions(owner,subject,difficulty,question,options,answer,explanation,approved,created_at) VALUES(NULL,?,?,?,?,?,?,1,?)",
                          (s,d,q,json.dumps(o,ensure_ascii=False),a,e,datetime.now().isoformat(timespec="seconds")))
init_db()

# ---------- Style ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
.stApp {background: radial-gradient(circle at 8% 0%, #30215f 0, #141832 42%, #090d1d 100%); color:#f7f7ff;font-family:Inter,sans-serif}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#171936,#101326);border-right:1px solid #37365f}
h1,h2,h3 {color:#f7f4ff}
div.stButton>button,div.stDownloadButton>button {border:0;border-radius:12px;background:linear-gradient(100deg,#6847ff,#b04bff);color:white;font-weight:700;min-height:2.6rem;transition:all .2s}
div.stButton>button:hover,div.stDownloadButton>button:hover {border:1px solid #e1c8ff;color:white;transform:translateY(-1px)}
[data-testid="stMetric"] {background:rgba(27,32,68,.88);border:1px solid #393968;padding:15px;border-radius:14px;box-shadow:0 8px 24px rgba(0,0,0,.12)}
.panel {background:linear-gradient(135deg,rgba(37,40,83,.95),rgba(25,26,55,.95));border:1px solid #4b4780;border-radius:18px;padding:20px;margin:8px 0;box-shadow:0 10px 30px rgba(0,0,0,.12);animation:fadeUp .35s ease-out}
.small {color:#c7c9ed}
@keyframes fadeUp {from {opacity:0;transform:translateY(6px)} to {opacity:1;transform:translateY(0)}}
@media (max-width: 700px) {
  .block-container {padding-top:1rem;padding-left:1rem;padding-right:1rem}
  h1 {font-size:1.8rem!important} h2 {font-size:1.4rem!important}
  [data-testid="stMetric"] {padding:10px}
  .panel {padding:14px;border-radius:14px}
}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def user_by_name(username):
    with db() as c:
        r=c.execute("SELECT * FROM users WHERE username=?",(username,)).fetchone()
    return dict(r) if r else None

def questions(subject="Barcha fanlar", difficulty="Barcha darajalar", approved=True):
    sql="SELECT * FROM questions WHERE 1=1"; args=[]
    if approved: sql+=" AND approved=1"
    if subject!="Barcha fanlar": sql+=" AND subject=?"; args.append(subject)
    if difficulty!="Barcha darajalar": sql+=" AND difficulty=?"; args.append(difficulty)
    with db() as c: rows=c.execute(sql+" ORDER BY id DESC",args).fetchall()
    out=[]
    for row in rows:
        q=dict(row); q["options"]=json.loads(q["options"]); out.append(q)
    return out

def add_question(owner, subject, difficulty, question, options, answer, explanation, approved=1):
    with db() as c:
        c.execute("""INSERT INTO questions(owner,subject,difficulty,question,options,answer,explanation,approved,created_at)
        VALUES(?,?,?,?,?,?,?,?,?)""",(owner,subject,difficulty,question,json.dumps(options,ensure_ascii=False),answer,explanation,approved,datetime.now().isoformat(timespec="seconds")))

def award(user_id, xp, coins):
    with db() as c:
        c.execute("UPDATE users SET xp=xp+?,coins=coins+? WHERE id=?",(xp,coins,user_id))
        row=c.execute("SELECT xp FROM users WHERE id=?",(user_id,)).fetchone()
        total=row["xp"]
        if total>=100 and total-xp<100: c.execute("INSERT OR IGNORE INTO achievements VALUES(?,?,?)",(user_id,"Birinchi 100 XP",datetime.now().isoformat(timespec="seconds")))
        if total>=500 and total-xp<500: c.execute("INSERT OR IGNORE INTO achievements VALUES(?,?,?)",(user_id,"500 XP klubi",datetime.now().isoformat(timespec="seconds")))

def new_code():
    return "".join(random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(6))

# ---------- Session ----------
defaults={"user":None,"quiz":None,"qi":0,"score":0,"correct":0,"streak":0,"answered":False,"selected":None,
          "finished":False,"qresults":[],"deadline":None,"assignment_mode":False,"assignment_id":None}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

def login_screen():
    st.markdown("# 🎮 Quiz Arena **PRO**")
    st.markdown("### Bilimni o‘yin bilan kuchaytir! 🚀")
    st.write("O‘qituvchilar, o‘quvchilar va sinflar uchun interaktiv ta’lim maydoni.")
    l,r=st.columns(2)
    with l:
        st.markdown('<div class="panel"><h3>🔐 Tizimga kirish</h3></div>',unsafe_allow_html=True)
        with st.form("login_form"):
            username=st.text_input("Login")
            password=st.text_input("Parol",type="password")
            submit=st.form_submit_button("Kirish")
        if submit:
            u=user_by_name(username.strip())
            if u and u["password"]==hpass(password):
                st.session_state.user=u; st.rerun()
            else: st.error("Login yoki parol noto‘g‘ri.")
    with r:
        st.markdown('<div class="panel"><h3>✨ Yangi hisob</h3></div>',unsafe_allow_html=True)
        with st.form("register_form"):
            name=st.text_input("Ism-familiya",key="rname")
            username=st.text_input("Yangi login",key="ruser")
            password=st.text_input("Parol (kamida 8 belgi)",type="password",key="rpass")
            role=st.selectbox("Rol",["student","teacher"],format_func=lambda x:"🎓 O‘quvchi" if x=="student" else "👩‍🏫 O‘qituvchi")
            submit=st.form_submit_button("Hisob yaratish")
        if submit:
            if not name.strip() or not username.strip() or len(password)<8:
                st.error("Ism, login kiriting va kamida 8 belgili parol tanlang.")
            elif user_by_name(username.strip()): st.error("Bu login band.")
            else:
                try:
                    with db() as c:
                        c.execute("INSERT INTO users(username,password,name,role,created_at) VALUES(?,?,?,?,?)",
                                  (username.strip(),hpass(password),name.strip(),role,datetime.now().isoformat(timespec="seconds")))
                    st.success("Hisob yaratildi! Endi tizimga kiring.")
                except sqlite3.IntegrityError: st.error("Bu login band.")

def finish_quiz():
    u=st.session_state.user; qs=st.session_state.quiz
    subject=qs[0]["subject"] if len(set(q["subject"] for q in qs))==1 else "Aralash"
    with db() as c:
        c.execute("INSERT INTO results(user_id,score,correct,total,subject,played_at) VALUES(?,?,?,?,?,?)",
                  (u["id"],st.session_state.score,st.session_state.correct,len(qs),subject,datetime.now().strftime("%Y-%m-%d %H:%M")))
    award(u["id"],st.session_state.correct*50,st.session_state.correct*10)
    st.session_state.finished=True
    st.session_state.deadline=None

# ---------- Auth ----------
if not st.session_state.user:
    login_screen()
    st.stop()
u=user_by_name(st.session_state.user["username"])
st.session_state.user=u
teacher=u["role"]=="teacher"

with st.sidebar:
    st.markdown("# 🎮 QUIZ ARENA")
    st.caption("PRO · LEARN · PLAY · WIN")
    st.write(f"Salom, **{u['name']}**")
    st.caption("👩‍🏫 O‘qituvchi" if teacher else "🎓 O‘quvchi")
    if teacher:
        menu=["🏠 Bosh sahifa","👩‍🏫 O‘qituvchi paneli","📝 Savollar banki","➕ Savol yaratish","🤖 AI test yordamchisi","📂 Import / eksport","⚡ Kahoot Live","🎵 Musiqa","🏆 Reyting va natijalar","🎨 Dizayn"]
    else:
        menu=["🏠 Bosh sahifa","🎮 Quiz o‘ynash","⚡ Kahoot Live","🎵 Musiqa","📚 Uy vazifalari","🔑 Sinfga qo‘shilish","💡 Savol taklif qilish","🏆 Reyting va natijalar","🎨 Dizayn"]
    page=st.radio("ASOSIY MENYU",menu)
    st.divider()
    st.metric("⭐ XP",u["xp"]); st.metric("🪙 Tangalar",u["coins"]); st.metric("🏅 Daraja",u["xp"]//300+1)
    if st.button("🚪 Chiqish"):
        st.session_state.user=None
        for k,v in defaults.items(): st.session_state[k]=v
        st.rerun()

if page=="🏠 Bosh sahifa":
    st.markdown("# 🌌 Quiz Arena PRO")
    st.markdown("### Bilim — sening super kuching! ✨")
    st.markdown(f'<div class="panel"><h2>Xush kelibsiz, {u["name"]}! 🚀</h2><p>Viktorinalarda qatnashing, vazifalarni bajaring va yangi darajalarga chiqing.</p></div>',unsafe_allow_html=True)
    with db() as c:
        totalq=c.execute("SELECT COUNT(*) FROM questions WHERE approved=1").fetchone()[0]
        totalusers=c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        myplays=c.execute("SELECT COUNT(*) FROM results WHERE user_id=?",(u["id"],)).fetchone()[0]
    a,b,c=st.columns(3); a.metric("📚 Savollar",totalq); b.metric("👥 Foydalanuvchilar",totalusers); c.metric("🎯 O‘yinlarim",myplays)
    x,y,z=st.columns(3)
    x.markdown('<div class="panel"><h3>🎮 O‘yna</h3><p>Turli fanlarda bilimingni sinab ko‘r.</p></div>',unsafe_allow_html=True)
    y.markdown('<div class="panel"><h3>⚡ Rivojlan</h3><p>XP to‘pla, daraja oshir, rekord o‘rnat.</p></div>',unsafe_allow_html=True)
    z.markdown('<div class="panel"><h3>🏆 Yetakchi bo‘l</h3><p>Reytingdagi o‘rningni ko‘r.</p></div>',unsafe_allow_html=True)
    st.info("Maslahat: o‘qituvchilar sinf yaratib, kodni o‘quvchilarga ulashishi mumkin.")

elif page=="👩‍🏫 O‘qituvchi paneli":
    st.title("👩‍🏫 O‘qituvchi boshqaruv markazi")
    with st.form("class_form"):
        cname=st.text_input("Yangi sinf nomi",placeholder="7-A / Informatika")
        make=st.form_submit_button("➕ Sinf yaratish")
    if make:
        if not cname.strip(): st.error("Sinf nomini kiriting.")
        else:
            code=new_code()
            with db() as c: c.execute("INSERT INTO classes(teacher,name,code,created_at) VALUES(?,?,?,?)",(u["id"],cname.strip(),code,datetime.now().isoformat(timespec="seconds")))
            st.success(f"Sinf yaratildi! O‘quvchilarga kodni bering: **{code}**")
    with db() as c: classes=c.execute("SELECT * FROM classes WHERE teacher=? ORDER BY id DESC",(u["id"],)).fetchall()
    if not classes: st.info("Hozircha sinf yo‘q. Yuqoridagi forma orqali yarating.")
    for cl in classes:
        with st.expander(f"🏫 {cl['name']} · KOD: {cl['code']}"):
            st.code(cl["code"])
            with db() as c:
                members=c.execute("SELECT users.name,users.username,users.xp FROM members JOIN users ON users.id=members.student WHERE class_id=? ORDER BY users.xp DESC",(cl["id"],)).fetchall()
                assigns=c.execute("SELECT * FROM assignments WHERE class_id=? ORDER BY id DESC",(cl["id"],)).fetchall()
            st.subheader(f"👥 O‘quvchilar ({len(members)})")
            if members: st.dataframe([{"Ism":m["name"],"Login":m["username"],"XP":m["xp"]} for m in members],use_container_width=True)
            else: st.caption("O‘quvchilar hali qo‘shilmagan.")
            st.subheader("📝 Uy vazifasi yaratish")
            subjects=sorted(set(q["subject"] for q in questions()))
            with st.form(f"assign_{cl['id']}"):
                title=st.text_input("Vazifa nomi",key=f"atitle{cl['id']}")
                subject=st.selectbox("Fan",subjects,key=f"asub{cl['id']}")
                count=st.slider("Savollar soni",1, min(20,max(1,len(questions(subject)))), min(5,max(1,len(questions(subject)))),key=f"acount{cl['id']}")
                due=st.date_input("Topshirish sanasi",value=date.today(),key=f"adue{cl['id']}")
                create=st.form_submit_button("Vazifani tayinlash")
            if create:
                pool=questions(subject)
                if title.strip() and pool:
                    qs=random.sample(pool,min(count,len(pool)))
                    with db() as c:
                        c.execute("INSERT INTO assignments(class_id,title,subject,questions,due,created_at) VALUES(?,?,?,?,?,?)",
                                  (cl["id"],title.strip(),subject,json.dumps(qs,ensure_ascii=False),str(due),datetime.now().isoformat(timespec="seconds")))
                    st.success("Vazifa tayinlandi!")
                    st.rerun()
                else: st.error("Vazifa nomini kiriting yoki savollar qo‘shing.")
            st.subheader("📈 Vazifa natijalari")
            for ass in assigns:
                st.write(f"**{ass['title']}** · {ass['subject']} · muddat: {ass['due'] or '—'}")
                with db() as c:
                    marks=c.execute("SELECT users.name,users.username,score,correct,total,submitted_at FROM assignment_results JOIN users ON users.id=student WHERE assignment_id=? ORDER BY score DESC",(ass["id"],)).fetchall()
                if marks: st.dataframe([{"O‘quvchi":m["name"],"Login":m["username"],"Ball":m["score"],"To‘g‘ri":f"{m['correct']}/{m['total']}","Topshirgan vaqt":m["submitted_at"]} for m in marks],use_container_width=True)
                else: st.caption("Hali topshirilmagan.")

elif page=="🎮 Quiz o‘ynash":
    st.title("🎮 Quiz Arena")
    if st.session_state.finished and st.session_state.quiz is not None:
        qs=st.session_state.quiz
        st.balloons()
        st.success(f"Natija: {st.session_state.score} ball · {st.session_state.correct}/{len(qs)} to‘g‘ri")
        for r in st.session_state.qresults:
            st.write(("✅ " if r["correct"] else "❌ ")+r["question"])
            st.caption(f"Javob: {r['answer']} · Sizning javobingiz: {r['selected']} · {r['explanation']}")
        if st.button("Yana o‘ynash"):
            st.session_state.quiz=None; st.session_state.finished=False; st.rerun()
    elif st.session_state.quiz is None:
        subjects=sorted(set(q["subject"] for q in questions()))
        with st.form("start_quiz"):
            subject=st.selectbox("Fan",["Barcha fanlar"]+subjects)
            diff=st.selectbox("Qiyinlik",["Barcha darajalar","Oson","O‘rta","Qiyin"])
            pool=questions(subject,diff)
            count=st.slider("Savollar soni",1,max(1,min(30,len(pool))),min(5,max(1,len(pool))))
            sec=st.select_slider("Har savol uchun vaqt",options=[10,15,20,30,45,60],value=15)
            start=st.form_submit_button("🚀 O‘yinni boshlash")
        if start:
            if not pool: st.error("Bu tanlovda savol topilmadi.")
            else:
                st.session_state.quiz=random.sample(pool,min(count,len(pool)))
                st.session_state.qi=0; st.session_state.score=0; st.session_state.correct=0; st.session_state.streak=0
                st.session_state.answered=False; st.session_state.selected=None; st.session_state.finished=False
                st.session_state.qresults=[]; st.session_state.time_per_q=sec
                st.session_state.deadline=time.time()+sec
                st.rerun()
    else:
        qs=st.session_state.quiz; i=st.session_state.qi; q=qs[i]
        # Browser-side periodic rerun updates the countdown without blocking the server.
        if not st.session_state.answered:
            st_autorefresh(interval=1000, limit=None, key="quiz_countdown_refresh")
        if not st.session_state.answered and st.session_state.deadline is None:
            st.session_state.deadline=time.time()+st.session_state.get("time_per_q",15)
        left=max(0,int(st.session_state.deadline-time.time())) if not st.session_state.answered else 0
        st.progress((i+1)/len(qs),text=f"Savol {i+1}/{len(qs)}")
        a,b,c=st.columns(3); a.metric("⭐ Ball",st.session_state.score); b.metric("🔥 Combo",st.session_state.streak); c.metric("⏱️ Qolgan vaqt",f"{left} s")
        st.markdown(f'<div class="panel"><h2>{q["question"]}</h2><p>{q["subject"]} · {q["difficulty"]}</p></div>',unsafe_allow_html=True)
        if not st.session_state.answered and left<=0:
            st.session_state.answered=True; st.session_state.selected=None; st.session_state.streak=0
            st.session_state.qresults.append({"question":q["question"],"selected":"Vaqt tugadi","answer":q["answer"],"correct":False,"explanation":q["explanation"]})
            st.rerun()
        if not st.session_state.answered:
            for j,opt in enumerate(q["options"]):
                if st.button(f"{chr(65+j)} · {opt}",key=f"opt_{i}_{j}"):
                    ok=opt==q["answer"]; st.session_state.selected=opt; st.session_state.answered=True
                    if ok:
                        st.session_state.streak+=1; st.session_state.correct+=1
                        st.session_state.score+=100+min(st.session_state.streak-1,5)*20+left
                    else: st.session_state.streak=0
                    st.session_state.qresults.append({"question":q["question"],"selected":opt,"answer":q["answer"],"correct":ok,"explanation":q["explanation"]})
                    st.rerun()
        else:
            if st.session_state.selected==q["answer"]: st.success("✅ To‘g‘ri javob!")
            elif st.session_state.selected is None: st.warning(f"⏰ Vaqt tugadi! To‘g‘ri javob: {q['answer']}")
            else: st.error(f"❌ To‘g‘ri javob: {q['answer']}")
            st.info("💡 "+q["explanation"])
            if st.button("➡️ Keyingi savol",key=f"next_{i}"):
                if i+1<len(qs):
                    st.session_state.qi+=1; st.session_state.answered=False; st.session_state.selected=None
                    st.session_state.deadline=time.time()+st.session_state.get("time_per_q",15); st.rerun()
                else:
                    finish_quiz(); st.rerun()

elif page=="📚 Uy vazifalari":
    st.title("📚 Mening uy vazifalarim")
    with db() as c:
        classes=c.execute("SELECT classes.* FROM classes JOIN members ON members.class_id=classes.id WHERE members.student=?",(u["id"],)).fetchall()
    if not classes: st.info("Hozircha sinfga qo‘shilmagansiz. «Sinfga qo‘shilish» bo‘limida kod kiriting.")
    for cl in classes:
        st.subheader("🏫 "+cl["name"])
        with db() as c: assigns=c.execute("SELECT * FROM assignments WHERE class_id=? ORDER BY id DESC",(cl["id"],)).fetchall()
        for ass in assigns:
            with st.expander(f"📝 {ass['title']} · {ass['subject']} · muddat {ass['due'] or '—'}"):
                with db() as c: done=c.execute("SELECT * FROM assignment_results WHERE assignment_id=? AND student=?",(ass["id"],u["id"])).fetchone()
                if done: st.success(f"Topshirilgan: {done['score']} ball ({done['correct']}/{done['total']})")
                else:
                    qs=json.loads(ass["questions"])
                    with st.form(f"homework_{ass['id']}"):
                        answers=[st.radio(f"{i+1}. {q['question']}",q["options"],key=f"hw_{ass['id']}_{i}") for i,q in enumerate(qs)]
                        submit=st.form_submit_button("✅ Vazifani topshirish")
                    if submit:
                        correct=sum(answers[i]==q["answer"] for i,q in enumerate(qs))
                        with db() as c:
                            c.execute("INSERT INTO assignment_results(assignment_id,student,score,correct,total,submitted_at) VALUES(?,?,?,?,?,?)",
                                      (ass["id"],u["id"],correct*100,correct,len(qs),datetime.now().isoformat(timespec="seconds")))
                        award(u["id"],correct*50,correct*10)
                        st.success(f"Natija: {correct}/{len(qs)}"); st.rerun()

elif page=="🔑 Sinfga qo‘shilish":
    st.title("🔑 Sinfga qo‘shilish")
    with st.form("join_class"):
        code=st.text_input("O‘qituvchi bergan 6 belgili kod").strip().upper()
        go=st.form_submit_button("Sinfga qo‘shilish")
    if go:
        with db() as c: cl=c.execute("SELECT * FROM classes WHERE code=?",(code,)).fetchone()
        if not cl: st.error("Kod topilmadi. O‘qituvchidan tekshirib oling.")
        else:
            try:
                with db() as c: c.execute("INSERT INTO members(class_id,student,joined_at) VALUES(?,?,?)",(cl["id"],u["id"],datetime.now().isoformat(timespec="seconds")))
                st.success(f"«{cl['name']}» sinfiga qo‘shildingiz.")
            except sqlite3.IntegrityError: st.info("Siz bu sinfga avval qo‘shilgansiz.")

elif page in ["➕ Savol yaratish","💡 Savol taklif qilish"]:
    st.title("➕ Savollar banki")
    approved=1 if teacher else 0
    with st.form("question_form"):
        subject=st.text_input("Fan / mavzu","Informatika")
        diff=st.selectbox("Qiyinlik",["Oson","O‘rta","Qiyin"])
        question=st.text_area("Savol matni")
        opts=[st.text_input(f"{chr(65+i)} varianti",key=f"qopt{i}") for i in range(4)]
        ai=st.selectbox("To‘g‘ri javob",range(4),format_func=lambda i:f"{chr(65+i)} · {opts[i] or 'Variant'}")
        explanation=st.text_area("Javob izohi")
        submit=st.form_submit_button("Saqlash")
    if submit:
        if not question.strip() or any(not x.strip() for x in opts): st.error("Savol va 4 variantni to‘ldiring.")
        else:
            add_question(u["id"],subject.strip(),diff,question.strip(),opts,opts[ai],explanation.strip(),approved)
            st.success("Savol qo‘shildi." if teacher else "Savol o‘qituvchi ko‘rib chiqishi uchun yuborildi.")
    if teacher:
        st.subheader("🛡️ Tasdiq kutayotgan savollar")
        pending=questions(approved=False)
        pending=[q for q in pending if not q["approved"]]
        if pending:
            for q in pending:
                with st.expander(q["question"]):
                    st.write(q["subject"],q["difficulty"],q["options"],"Javob:",q["answer"])
                    if st.button("Tasdiqlash",key=f"approve{q['id']}"):
                        with db() as c: c.execute("UPDATE questions SET approved=1 WHERE id=?",(q["id"],))
                        st.rerun()
        else: st.caption("Tasdiq kutayotgan savol yo‘q.")

elif page=="📝 Savollar banki":
    st.title("📝 Savollar banki")
    with db() as c: rows=c.execute("SELECT * FROM questions ORDER BY id DESC").fetchall()
    if rows:
        st.dataframe([{"ID":r["id"],"Fan":r["subject"],"Daraja":r["difficulty"],"Savol":r["question"],"Tasdiqlangan":bool(r["approved"])} for r in rows],use_container_width=True)
        with st.form("deleteq"):
            qid=st.number_input("O‘chirish uchun savol ID",min_value=1,step=1)
            delete=st.form_submit_button("Savolni o‘chirish")
        if delete:
            with db() as c: c.execute("DELETE FROM questions WHERE id=?",(int(qid),))
            st.success("Agar ID mavjud bo‘lsa, savol o‘chirildi."); st.rerun()

elif page in ["🤖 AI test yordamchisi"]:
    st.title("🤖 AI test yordamchisi")
    st.markdown('<div class="panel"><h3>Haqiqiy AI yordamida test yaratish</h3><p>Mavzu, sinf darajasi va savollar sonini tanlang. AI savol, 4 ta variant, to‘g‘ri javob va izoh tayyorlaydi. Saqlashdan oldin natijani tekshiring.</p></div>', unsafe_allow_html=True)
    api_default = os.getenv("OPENAI_API_KEY", "")
    api_key = st.text_input("OpenAI API kaliti", value=api_default, type="password", help="Kalit faqat shu sessiyada ishlatiladi. Uni boshqalarga yubormang.")
    st.caption("API kaliti bo‘lmasa, AI generatsiyasi ishlamaydi. Qolgan platforma funksiyalari odatdagidek ishlayveradi.")
    with st.form("ai_builder"):
        topic=st.text_input("Mavzu",placeholder="Masalan: Python’da sikllar")
        count=st.slider("Nechta savol?",1,20,5)
        level=st.selectbox("Qiyinlik",["Oson","O‘rta","Qiyin"])
        grade=st.selectbox("Sinf / daraja",["Boshlang‘ich","5–7-sinf","8–9-sinf","10–11-sinf","Talabalar / kattalar"])
        language=st.selectbox("Savollar tili",["O‘zbek tili","Русский язык","English"])
        generate=st.form_submit_button("✨ AI orqali savollar yaratish")
    if generate:
        if not topic.strip():
            st.error("Mavzu kiriting.")
        elif not api_key.strip():
            st.error("Haqiqiy AI ishlashi uchun OpenAI API kalitini kiriting. Kalitni platforma ichida doimiy saqlamaymiz.")
        else:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key.strip())
                prompt = f"""Create exactly {count} high-quality multiple-choice quiz questions in {language} about: {topic.strip()}.
Audience: {grade}. Difficulty: {level}. Return ONLY valid JSON, no markdown, with this schema:
{{"questions":[{{"question":"...","options":["A","B","C","D"],"answer":"exactly one option text","explanation":"brief explanation"}}]}}
Requirements: factual, distinct questions; exactly 4 plausible options per question; answer must exactly match one option; explanation in the requested language; do not invent facts; avoid repeated questions."""
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"system","content":"You create accurate educational multiple-choice questions. Follow the requested JSON schema exactly."},{"role":"user","content":prompt}],
                    response_format={"type":"json_object"},
                    temperature=0.4,
                )
                payload = json.loads(response.choices[0].message.content or "{}")
                raw_questions = payload.get("questions", [])
                draft=[]
                for item in raw_questions:
                    opts=item.get("options", [])
                    answer=item.get("answer", "")
                    question=item.get("question", "").strip()
                    if question and isinstance(opts,list) and len(opts)==4 and answer in opts:
                        draft.append({"subject":topic.strip(),"difficulty":level,"question":question,"options":opts,"answer":answer,"explanation":item.get("explanation","")})
                if len(draft) != count:
                    st.warning(f"AI {count} ta so‘ralgan savoldan {len(draft)} tasini tekshiruvdan o‘tkazdi. Natijani ko‘rib chiqing yoki qayta yarating.")
                if draft:
                    st.session_state.ai_draft=draft
                    st.success(f"{len(draft)} ta AI savoli yaratildi. Saqlashdan oldin tekshiring.")
                else:
                    st.error("AI javobi kerakli formatda kelmadi. Qayta urinib ko‘ring.")
            except ImportError:
                st.error("OpenAI kutubxonasi topilmadi. Terminalda: python -m pip install -r requirements.txt buyrug‘ini bajaring.")
            except Exception as e:
                st.error(f"AI so‘rovida xato yuz berdi: {e}")
    if st.session_state.get("ai_draft"):
        st.subheader("🧪 Yaratilgan savollarni tekshirish")
        st.warning("AI yaratgan savollarni darsda ishlatishdan oldin mazmunan tekshiring.")
        for i, q in enumerate(st.session_state.ai_draft, 1):
            with st.expander(f"{i}. {q['question']}", expanded=(i == 1)):
                st.write("**Variantlar:**")
                for option in q["options"]:
                    st.write(("✅ " if option == q["answer"] else "• ") + option)
                st.write("**Izoh:**", q["explanation"])
        if st.button("💾 Barcha savollarni bankka saqlash"):
            for q in st.session_state.ai_draft:
                add_question(u["id"],q["subject"],q["difficulty"],q["question"],q["options"],q["answer"],q["explanation"],1)
            st.session_state.ai_draft=[]
            st.success("Savollar bankka saqlandi.")
            st.rerun()

elif page=="📂 Import / eksport":
    st.title("📂 Savollar importi va eksporti")
    uploaded=st.file_uploader("JSON yoki CSV faylni tanlang",type=["json","csv"])
    if uploaded:
        try:
            if uploaded.name.lower().endswith(".json"):
                data=json.load(uploaded)
                if isinstance(data,dict): data=data.get("questions",[])
            else:
                data=[]
                for row in csv.DictReader(io.StringIO(uploaded.getvalue().decode("utf-8-sig"))):
                    raw=row.get("options","")
                    row["options"]=json.loads(raw) if raw.strip().startswith("[") else raw.split("|")
                    data.append(row)
            if st.button("📥 Import qilish"):
                added=0
                for q in data:
                    opts=q.get("options",[])
                    if q.get("question") and len(opts)==4 and q.get("answer") in opts:
                        add_question(u["id"],q.get("subject",q.get("category","Umumiy")),q.get("difficulty","Oson"),q["question"],opts,q["answer"],q.get("explanation",""),1)
                        added+=1
                st.success(f"{added} ta savol import qilindi.")
        except Exception as e: st.error(f"Faylni o‘qishda xato: {e}")
    qs=questions(approved=False)
    export=[{k:q[k] for k in ["subject","difficulty","question","options","answer","explanation"]} for q in qs]
    st.download_button("⬇️ JSON yuklab olish",json.dumps({"questions":export},ensure_ascii=False,indent=2),"quiz_questions.json","application/json")
    out=io.StringIO(); w=csv.DictWriter(out,fieldnames=["subject","difficulty","question","options","answer","explanation"]); w.writeheader()
    for q in export:
        row=q.copy(); row["options"]=json.dumps(row["options"],ensure_ascii=False); w.writerow(row)
    st.download_button("⬇️ CSV yuklab olish",out.getvalue(),"quiz_questions.csv","text/csv")

elif page=="🏆 Reyting va natijalar":
    st.title("🏆 Reyting va natijalar")
    with db() as c:
        leaders=c.execute("SELECT id,name,role,xp,coins FROM users ORDER BY xp DESC,coins DESC LIMIT 20").fetchall()
        mine=c.execute("SELECT * FROM results WHERE user_id=? ORDER BY id DESC LIMIT 20",(u["id"],)).fetchall()
        badges=c.execute("SELECT badge,earned_at FROM achievements WHERE user_id=? ORDER BY earned_at DESC",(u["id"],)).fetchall()
    a,b,c=st.columns(3); a.metric("⭐ XP",u["xp"]); b.metric("🪙 Tangalar",u["coins"]); c.metric("🏅 Daraja",u["xp"]//300+1)
    st.subheader("🥇 TOP 20")
    st.dataframe([{"O‘rin":i+1,"Ism":r["name"],"Rol":"O‘quvchi" if r["role"]=="student" else "O‘qituvchi","XP":r["xp"],"Tangalar":r["coins"]} for i,r in enumerate(leaders)],use_container_width=True)
    st.subheader("📈 Mening so‘nggi o‘yinlarim")
    if mine: st.dataframe([{"Sana":r["played_at"],"Fan":r["subject"],"Ball":r["score"],"To‘g‘ri":f"{r['correct']}/{r['total']}"} for r in mine],use_container_width=True)
    else: st.info("Hali o‘yin natijalari yo‘q.")
    st.subheader("🎖️ Yutuqlar")
    if badges:
        for b in badges: st.write(f"🏅 {b['badge']} · {b['earned_at'][:10]}")
    else: st.caption("Yutuqlar XP to‘plaganingizda ochiladi.")

elif page=="⚡ Kahoot Live":
    # Refresh the live room view so hosts and players see updates promptly.
    st_autorefresh(interval=2500, limit=None, key="live_room_refresh")
    st.title("⚡ Kahoot uslubidagi jonli viktorina")
    st.caption("O‘qituvchi xona yaratadi va kodni ulashadi. O‘quvchilar kod bilan kirib, bir vaqtda javob berishadi.")
    if teacher:
        st.subheader("🎤 O‘yin xonasi yaratish")
        subjects=sorted(set(q["subject"] for q in questions()))
        with st.form("live_create"):
            title=st.text_input("Viktorina nomi", "Sinf bilan jonli quiz")
            subject=st.selectbox("Fan", ["Barcha fanlar"]+subjects)
            count=st.slider("Savollar soni", 3, min(20,max(3,len(questions(subject)))), min(10,max(3,len(questions(subject)))))
            create_live=st.form_submit_button("🚀 Xona yaratish")
        if create_live:
            pool=questions(subject)
            if len(pool)<1 or not title.strip():
                st.error("Viktorina nomi va savollar kerak.")
            else:
                selected=random.sample(pool,min(count,len(pool)))
                code=new_code()
                with db() as c:
                    c.execute("INSERT INTO live_rooms(host_id,code,title,questions,current_q,status,created_at) VALUES(?,?,?,?,?,?,?)",
                              (u["id"],code,title.strip(),json.dumps(selected,ensure_ascii=False),-1,"lobby",datetime.now().isoformat(timespec="seconds")))
                st.session_state.live_host_room=code
                st.success("Xona yaratildi! Kodni o‘quvchilarga ulashing.")
                st.rerun()
        with db() as c:
            rooms=c.execute("SELECT * FROM live_rooms WHERE host_id=? ORDER BY id DESC LIMIT 10",(u["id"],)).fetchall()
        for room in rooms:
            qs=json.loads(room["questions"])
            with st.expander(f"🎮 {room['title']} · {room['code']} · {room['status']}"):
                st.markdown(f"## Xona kodi: `{room['code']}`")
                st.write(f"Savollar: {len(qs)} · Holat: **{room['status']}**")
                with db() as c:
                    players=c.execute("""SELECT users.name,users.username,COALESCE(SUM(live_answers.points),0) AS points,
                        SUM(live_answers.correct) AS correct_count
                        FROM live_answers JOIN users ON users.id=live_answers.user_id
                        WHERE live_answers.room_id=? GROUP BY users.id ORDER BY points DESC""",(room["id"],)).fetchall()
                st.subheader(f"🏆 O‘yinchilar ({len(players)})")
                if players:
                    st.dataframe([{"O‘rin":i+1,"Ism":p["name"],"Ball":p["points"],"To‘g‘ri javoblar":p["correct_count"] or 0} for i,p in enumerate(players)],use_container_width=True)
                else:
                    st.info("O‘quvchilar kod orqali qo‘shilishini kuting.")
                if room["status"]=="lobby":
                    if st.button("▶️ O‘yinni boshlash",key=f"live_start_{room['id']}"):
                        with db() as c: c.execute("UPDATE live_rooms SET status='live',current_q=0 WHERE id=? AND host_id=?",(room["id"],u["id"]))
                        st.rerun()
                elif room["status"]=="live":
                    q=qs[room["current_q"]]
                    st.markdown(f"### Savol {room['current_q']+1}/{len(qs)}: {q['question']}")
                    st.write("**To‘g‘ri javob:**",q["answer"])
                    if st.button("➡️ Keyingi savol / yakunlash",key=f"live_next_{room['id']}"):
                        ni=room["current_q"]+1
                        with db() as c:
                            if ni>=len(qs): c.execute("UPDATE live_rooms SET status='finished' WHERE id=?",(room["id"],))
                            else: c.execute("UPDATE live_rooms SET current_q=? WHERE id=?",(ni,room["id"]))
                        st.rerun()
                else:
                    st.success("Viktorina yakunlandi.")
                    if players: st.balloons()

    st.divider()
    st.subheader("🎟️ O‘quvchi sifatida xonaga kirish")
    with st.form("live_join"):
        join_code=st.text_input("O‘qituvchi bergan xona kodi").strip().upper()
        join_live=st.form_submit_button("Xonaga kirish")
    if join_live:
        with db() as c: room=c.execute("SELECT * FROM live_rooms WHERE code=?",(join_code,)).fetchone()
        if not room: st.error("Bu kod bilan xona topilmadi.")
        elif room["status"]=="finished": st.error("Bu viktorina allaqachon yakunlangan.")
        else:
            st.session_state.live_room_id=room["id"]
            st.success(f"«{room['title']}» xonasiga kirdingiz.")
            st.rerun()

    rid=st.session_state.get("live_room_id")
    if rid:
        with db() as c: room=c.execute("SELECT * FROM live_rooms WHERE id=?",(rid,)).fetchone()
        if not room:
            st.session_state.live_room_id=None
        else:
            qs=json.loads(room["questions"])
            st.markdown(f'<div class="panel"><h2>🎮 {room["title"]}</h2><p>Xona kodi: {room["code"]}</p></div>',unsafe_allow_html=True)
            if room["status"]=="lobby":
                st.info("O‘qituvchi o‘yinni boshlashini kuting. Sahifani yangilab turing.")
            elif room["status"]=="finished":
                st.success("🏁 O‘yin tugadi! Yakuniy reyting:")
                with db() as c:
                    ranks=c.execute("""SELECT users.name,COALESCE(SUM(live_answers.points),0) points,
                        SUM(live_answers.correct) correct_count FROM live_answers JOIN users ON users.id=live_answers.user_id
                        WHERE room_id=? GROUP BY users.id ORDER BY points DESC""",(rid,)).fetchall()
                st.dataframe([{"O‘rin":i+1,"Ism":r["name"],"Ball":r["points"],"To‘g‘ri":r["correct_count"] or 0} for i,r in enumerate(ranks)],use_container_width=True)
            elif room["status"]=="live":
                qi=room["current_q"]; q=qs[qi]
                st.progress((qi+1)/len(qs),text=f"Savol {qi+1}/{len(qs)}")
                st.markdown(f'<div class="panel"><h2>{q["question"]}</h2></div>',unsafe_allow_html=True)
                with db() as c:
                    existing=c.execute("SELECT * FROM live_answers WHERE room_id=? AND user_id=? AND q_index=?",(rid,u["id"],qi)).fetchone()
                if existing:
                    st.success("Javobingiz qabul qilindi! O‘qituvchi keyingi savolga o‘tishini kuting.")
                    st.metric("Sizning ballingiz",existing["points"])
                else:
                    cols=st.columns(2)
                    for j,opt in enumerate(q["options"]):
                        if cols[j%2].button(f"{chr(65+j)} · {opt}",key=f"live_ans_{rid}_{qi}_{j}",use_container_width=True):
                            ok=(opt==q["answer"])
                            points=1000 if ok else 0
                            with db() as c:
                                try:
                                    c.execute("INSERT INTO live_answers(room_id,user_id,q_index,answer,correct,points,answered_at) VALUES(?,?,?,?,?,?,?)",
                                              (rid,u["id"],qi,opt,int(ok),points,datetime.now().isoformat(timespec="seconds")))
                                except sqlite3.IntegrityError: pass
                            if ok: award(u["id"],10,2)
                            st.rerun()
            if st.button("🔄 Holatni yangilash",key=f"live_refresh_{rid}"):
                st.rerun()

elif page=="🎵 Musiqa":
    st.title("🎵 Quiz Arena Music")
    st.markdown('<div class="panel"><h3>🎧 O‘qish yoki viktorina uchun musiqa</h3><p>O‘zingizdagi audio faylni qo‘ying yoki YouTube havolasi orqali tinglang.</p></div>',unsafe_allow_html=True)
    st.subheader("💿 Audio fayl")
    audio=st.file_uploader("MP3, WAV yoki OGG fayl yuklang",type=["mp3","wav","ogg","m4a"])
    if audio is not None:
        st.audio(audio.getvalue(),format=audio.type or "audio/mpeg")
    else:
        st.info("Audio faylni shu yerga yuklang — brauzerda ijro etiladi. Fayl serverga doimiy saqlanmaydi.")
    st.divider()
    st.subheader("▶️ YouTube musiqasi")
    yt=st.text_input("YouTube video havolasi",placeholder="https://www.youtube.com/watch?v=...")
    if yt.strip():
        import re as _re
        match=_re.search(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([A-Za-z0-9_-]{11})",yt.strip())
        if match:
            st.video("https://www.youtube.com/watch?v="+match.group(1))
        else:
            st.warning("YouTube havolasi noto‘g‘ri ko‘rinadi. Oddiy video havolasini kiriting.")
    st.caption("Eslatma: musiqa boshqa sahifaga o‘tganda davom etmasligi mumkin. YouTube ijrosi internet va videoning mavjudligiga bog‘liq.")

elif page=="🎨 Dizayn":
    st.title("🎨 Dizayn va ko‘rinish")
    theme=st.selectbox("Mavzu",["🌌 Neon galaktika","👾 Pixel-art","🌿 Tabiat","✨ Minimalist"], key="design_theme")
    themes={
      "🌌 Neon galaktika":("#141832","#6847ff","#b04bff","#30215f"),
      "👾 Pixel-art":("#101820","#00bfa6","#ff4f9a","#163b42"),
      "🌿 Tabiat":("#10251c","#248a59","#9acb45","#1b4934"),
      "✨ Minimalist":("#171923","#6478ff","#9b6bff","#292d3d")}
    bg,primary,secondary,glow=themes[theme]
    css = "<style>\n.stApp {background:radial-gradient(circle at 8% 0%, " + glow + " 0, " + bg + " 48%, #090d1d 100%)}\n"
    css += "div.stButton>button,div.stDownloadButton>button,[data-testid=\"stFormSubmitButton\"] button {background:linear-gradient(100deg," + primary + "," + secondary + ")}\n</style>"
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(f'<div class="panel"><h2>{theme}</h2><p>Tanlangan mavzu shu sessiyada qo‘llandi. Sahifa yangilanganda mavzuni qayta tanlashingiz mumkin.</p></div>',unsafe_allow_html=True)
    st.caption("Mavzu hozirgi sessiya uchun qo‘llanadi; doimiy profil sozlamasi sifatida saqlanmaydi.")

st.caption("Quiz Arena PRO · Streamlit + SQLite · AI savollar uchun OpenAI API kaliti talab qilinadi. Ommaviy foydalanish uchun hosting va doimiy umumiy ma’lumotlar bazasi sozlanishi kerak.")
