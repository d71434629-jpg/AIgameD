"""Quiz Arena PRO 2.0 — interfeys (Streamlit). Mantiq: core.py"""
import csv
import html
import io
import json
import math
import os
import random
import re
import time
from datetime import date, timedelta

import pandas as pd
import streamlit as st

import core as K
import games

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:  # kutubxona bo‘lmasa ham ilova ishlayveradi
    def st_autorefresh(*a, **k):
        return 0

esc = html.escape

# ============================================================== Mavzular (dizayn)
THEMES = {
    "neon": {"label": "🌌 Neon galaktika", "bg": "#141832", "p": "#6847ff", "s": "#b04bff", "glow": "#30215f",
             "radius": "14px", "font": "Inter, sans-serif", "head": "Inter, sans-serif"},
    "pixel": {"label": "👾 Pixel-art", "bg": "#0e1a14", "p": "#16a34a", "s": "#facc15", "glow": "#1d3b2a",
              "radius": "2px", "font": "'VT323', monospace", "head": "'Press Start 2P', cursive"},
    "nature": {"label": "🌿 Tabiat", "bg": "#10251c", "p": "#248a59", "s": "#9acb45", "glow": "#1b4934",
               "radius": "16px", "font": "Inter, sans-serif", "head": "Inter, sans-serif"},
    "sunset": {"label": "🌅 Quyosh botishi", "bg": "#2a1325", "p": "#ff5e62", "s": "#ff9966", "glow": "#5a1e3a",
               "radius": "16px", "font": "Inter, sans-serif", "head": "Inter, sans-serif"},
    "mono": {"label": "✨ Minimalist", "bg": "#171923", "p": "#6478ff", "s": "#9b6bff", "glow": "#292d3d",
             "radius": "10px", "font": "Inter, sans-serif", "head": "Inter, sans-serif"},
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Press+Start+2P&family=VT323&display=swap');
:root{--p:__P__;--s:__S__;--r:__R__}
.stApp{background:radial-gradient(circle at 8% 0%,__GLOW__ 0,__BG__ 45%,#070a16 100%);color:#f7f7ff;font-family:__FONT__}
h1,h2,h3,h4{color:#f7f4ff;font-family:__HEAD__}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#171936,#0f1224);border-right:1px solid #37365f}
div.stButton>button,div.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{border:0;border-radius:var(--r);
  background:linear-gradient(100deg,var(--p),var(--s));color:#fff;font-weight:700;min-height:2.6rem;transition:all .18s}
div.stButton>button:hover,div.stDownloadButton>button:hover,[data-testid="stFormSubmitButton"] button:hover{
  transform:translateY(-2px);box-shadow:0 8px 22px rgba(0,0,0,.35);color:#fff;border:0}
div.stButton>button:disabled{opacity:.45;transform:none;box-shadow:none}
[data-testid="stMetric"]{background:rgba(27,32,68,.85);border:1px solid #393968;padding:14px;border-radius:var(--r)}
.panel{background:linear-gradient(135deg,rgba(37,40,83,.95),rgba(25,26,55,.95));border:1px solid #4b4780;
  border-radius:calc(var(--r) + 4px);padding:20px;margin:8px 0;box-shadow:0 10px 30px rgba(0,0,0,.18);animation:fadeUp .35s ease-out}
.hero{display:flex;gap:18px;align-items:center;background:linear-gradient(110deg,var(--p),var(--s));
  border-radius:calc(var(--r) + 6px);padding:22px 26px;margin-bottom:12px;box-shadow:0 14px 40px rgba(0,0,0,.3)}
.hero h1{margin:0;font-size:1.9rem;color:#fff}.hero p{margin:.2rem 0 0;color:#fff;opacity:.92}
.hero-av{font-size:3.2rem;background:rgba(255,255,255,.2);border-radius:50%;width:84px;height:84px;display:flex;
  align-items:center;justify-content:center;flex:none}
.side-user{display:flex;gap:12px;align-items:center;margin-bottom:8px}
.side-user .av{font-size:2rem;background:rgba(255,255,255,.1);border-radius:50%;width:52px;height:52px;display:flex;
  align-items:center;justify-content:center}
.small{color:#c7c9ed;font-size:.85rem}
.chip{display:inline-block;padding:5px 14px;margin:3px;border-radius:999px;background:rgba(255,255,255,.12);
  border:1px solid rgba(255,255,255,.18);font-weight:600}
.bigcode{font-size:3rem;letter-spacing:.3em;font-weight:800;text-align:center;padding:12px 8px 12px 24px;margin:6px 0;
  border-radius:var(--r);background:rgba(255,255,255,.08);border:2px dashed rgba(255,255,255,.35);font-family:monospace}
.qtext{font-size:1.55rem;font-weight:700;line-height:1.35;margin:.2rem 0}
.qmeta{color:#c7c9ed;font-size:.9rem;margin-bottom:.3rem}
.opt{border-radius:var(--r);padding:14px 18px;margin:7px 0;font-weight:600;border:2px solid rgba(255,255,255,.16);
  background:rgba(255,255,255,.06)}
.opt.ok{border-color:#22c55e;background:rgba(34,197,94,.22)}
.opt.bad{border-color:#ef4444;background:rgba(239,68,68,.22)}
.opt.dim{opacity:.5}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:10px 0}
.tile{border-radius:var(--r);padding:20px 16px;font-size:1.25rem;font-weight:700;color:#fff;display:flex;gap:12px;
  align-items:center;box-shadow:0 6px 16px rgba(0,0,0,.28)}
.podium{display:flex;gap:12px;align-items:flex-end;justify-content:center;margin:14px 0 6px}
.pod{flex:1;max-width:210px;text-align:center;border-radius:var(--r) var(--r) 0 0;padding:12px 8px;
  background:linear-gradient(180deg,rgba(255,255,255,.18),rgba(255,255,255,.05));border:1px solid rgba(255,255,255,.2)}
.pod .em{font-size:2.4rem}.pod .nm{font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pod .pt{opacity:.85;font-size:.95rem}
.badge{display:inline-block;width:100%;box-sizing:border-box;padding:12px;margin:5px 0;border-radius:var(--r);
  background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.18)}
.badge.locked{filter:grayscale(1);opacity:.45}
.badge b{font-size:1rem}.badge span{display:block;font-size:.82rem;color:#c7c9ed}
[class*="st-key-qopt"] button{justify-content:flex-start;text-align:left;min-height:3.2rem;font-size:1.05rem;
  background:rgba(255,255,255,.08)!important;border:2px solid rgba(255,255,255,.2)!important}
[class*="st-key-qopt"] button:hover{border-color:var(--s)!important;background:rgba(255,255,255,.16)!important}
[class*="st-key-lva0_"] button{background:#e21b3c!important}
[class*="st-key-lva1_"] button{background:#1368ce!important}
[class*="st-key-lva2_"] button{background:#d89e00!important}
[class*="st-key-lva3_"] button{background:#26890c!important}
[class*="st-key-lva"] button{min-height:4.6rem;font-size:1.2rem;border-radius:var(--r)!important}
@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
@media (max-width:700px){
  .block-container{padding:1rem!important}
  h1{font-size:1.7rem!important}h2{font-size:1.35rem!important}
  .hero{padding:14px;gap:12px}.hero h1{font-size:1.3rem}.hero-av{width:58px;height:58px;font-size:2rem}
  .bigcode{font-size:2rem}.qtext{font-size:1.2rem}.tiles{grid-template-columns:1fr}
  .panel{padding:14px}
}
</style>
"""

PIXEL_EXTRA = """<style>
h1{font-size:1.5rem!important;line-height:1.5}h2{font-size:1.15rem!important;line-height:1.5}h3{font-size:.95rem!important}
.stApp,.stMarkdown p,label{font-size:1.25rem}
.panel,.hero,.opt,.tile,.chip,[data-testid="stMetric"]{border-radius:2px!important;box-shadow:4px 4px 0 rgba(0,0,0,.55)}
</style>"""

OPT_COLORS = ["#e21b3c", "#1368ce", "#d89e00", "#26890c"]
OPT_SHAPES = ["▲", "◆", "●", "■"]

TIPS = [
    "Har kuni 10 daqiqa takrorlash — haftada bir marta 2 soat o‘qishdan samaraliroq.",
    "Xato qilgan savollaringizni «Xatolarni qayta ishlash» rejimida takrorlang — shunda yaxshi eslab qolinadi.",
    "Pomodoro usuli: 25 daqiqa fokus, 5 daqiqa dam. «Musiqa va fokus» bo‘limida taymer bor.",
    "Javobni ovoz chiqarib tushuntirish — o‘zlashtirishning eng yaxshi tekshiruvi.",
    "Kunlik chaqiriqni ketma-ket bajarsangiz, har kuni ko‘proq tanga olasiz.",
    "Murakkab mavzuni kichik bo‘laklarga bo‘ling va har bo‘lak uchun alohida quiz yarating.",
    "Uxlashdan oldin 10 daqiqa takrorlash xotirada mustahkamlanadi.",
]

DEFAULTS = {"quiz": None, "qi": 0, "score": 0, "correct": 0, "streak": 0, "best_streak": 0, "answered": False,
            "selected": None, "finished": False, "qresults": [], "deadline": None, "time_per_q": 15,
            "quiz_mode": "normal", "hidden": None, "used_time": False, "finish_info": None, "wrong_qs": []}

# Menyu nomlari
M_HOME, M_PLAY, M_DAILY = "🏠 Bosh sahifa", "🎮 Quiz o‘ynash", "🔥 Kunlik chaqiriq"
M_LIVE, M_HW, M_JOIN = "⚡ Jonli viktorina", "📚 Uy vazifalari", "🔑 Sinfga qo‘shilish"
M_SUGGEST, M_RANK, M_MUSIC, M_PROFILE = "💡 Savol taklif qilish", "🏆 Reyting", "🎵 Musiqa va fokus", "👤 Profil va dizayn"
M_GAMES = "🕹️ O‘yinlar markazi"
T_PANEL, T_BANK, T_NEW = "👩‍🏫 O‘qituvchi paneli", "📝 Savollar banki", "➕ Savol yaratish"
T_AI, T_IO = "🤖 AI test yordamchisi", "📂 Import / eksport"


# ============================================================== Yordamchilar
def me():
    return st.session_state["_me"]


def secret(name, default=""):
    v = os.getenv(name)
    if v:
        return v
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def flash(msg, icon="✨"):
    st.session_state.setdefault("_flash", []).append((msg, icon))


def show_flash():
    for msg, icon in st.session_state.pop("_flash", []):
        st.toast(msg, icon=icon)


def notify(info):
    if not info:
        return
    if info.get("level_up"):
        flash(f"Yangi daraja: {info['level']}! 🎉", "🎉")
    for b in info.get("badges", []):
        icon, name, _ = K.BADGES[b]
        flash(f"Yangi yutuq: {name}", icon)


def goto(page):
    st.session_state["nav"] = page


def table(rows, **kw):
    if not rows:
        return
    try:
        st.dataframe(rows, width="stretch", hide_index=True, **kw)
    except Exception:
        st.dataframe(rows, use_container_width=True, hide_index=True, **kw)


def editor(df, **kw):
    try:
        return st.data_editor(df, width="stretch", **kw)
    except Exception:
        return st.data_editor(df, use_container_width=True, **kw)


def btn(label, **kw):
    try:
        return st.button(label, width="stretch", **kw)
    except TypeError:
        return st.button(label, use_container_width=True, **kw)


def count_slider(label, n, default, maxn, key):
    n = min(n, maxn)
    if n <= 0:
        return 0
    if n == 1:
        st.caption(f"{label}: 1")
        return 1
    return st.slider(label, 1, n, min(default, n), key=f"{key}_{n}")


def sel_subject(subject):
    return None if subject == "Barcha fanlar" else subject


def inject_css(theme_key):
    t = THEMES.get(theme_key, THEMES["neon"])
    css = CSS
    for k, v in (("__P__", t["p"]), ("__S__", t["s"]), ("__R__", t["radius"]), ("__GLOW__", t["glow"]),
                 ("__BG__", t["bg"]), ("__FONT__", t["font"]), ("__HEAD__", t["head"])):
        css = css.replace(k, v)
    st.markdown(css + (PIXEL_EXTRA if theme_key == "pixel" else ""), unsafe_allow_html=True)


def podium(rows, name="name", score="points", unit="ball"):
    """rows — kamayish tartibida. 2-1-3 ko‘rinishida chiqaradi."""
    if not rows:
        return
    medals = ["🥇", "🥈", "🥉"]
    heights = [150, 115, 90]
    order = [1, 0, 2]
    cells = ""
    for idx in order:
        if idx >= len(rows):
            continue
        r = rows[idx]
        cells += (f'<div class="pod" style="height:{heights[idx]}px"><div class="em">{esc(str(r.get("avatar") or medals[idx]))}</div>'
                  f'<div class="nm">{medals[idx]} {esc(str(r[name]))}</div><div class="pt">{r[score]} {unit}</div></div>')
    st.markdown(f'<div class="podium">{cells}</div>', unsafe_allow_html=True)


@st.cache_resource
def boot():
    K.init_db()
    return True


# ============================================================== Kirish / ro‘yxatdan o‘tish
def login_screen():
    st.markdown('<div class="hero"><div class="hero-av">🎮</div><div><h1>Quiz Arena PRO</h1>'
                '<p>Bilimni o‘yin bilan kuchaytir! O‘qituvchilar, o‘quvchilar va sinflar uchun interaktiv maydon.</p></div></div>',
                unsafe_allow_html=True)
    teacher_code = secret("QUIZ_ARENA_TEACHER_CODE")
    t_login, t_reg = st.tabs(["🔐 Kirish", "✨ Yangi hisob"])
    with t_login:
        with st.form("login_form"):
            username = st.text_input("Login")
            password = st.text_input("Parol", type="password")
            go = st.form_submit_button("Kirish")
        if go:
            if not username.strip():
                st.error("Loginni kiriting.")
            elif K.too_many_attempts(username.strip()):
                st.error("Juda ko‘p noto‘g‘ri urinish. Bir necha daqiqadan so‘ng qayta urinib ko‘ring.")
            else:
                user = K.authenticate(username, password)
                if user:
                    st.session_state["uid"] = user["id"]
                    st.rerun()
                else:
                    st.error("Login yoki parol noto‘g‘ri.")
    with t_reg:
        with st.form("register_form"):
            name = st.text_input("Ism-familiya", key="rname")
            username = st.text_input("Yangi login", key="ruser")
            password = st.text_input("Parol (kamida 8 belgi)", type="password", key="rpass")
            c1, c2 = st.columns(2)
            role = c1.selectbox("Rol", ["student", "teacher"],
                                format_func=lambda x: "🎓 O‘quvchi" if x == "student" else "👩‍🏫 O‘qituvchi")
            avatar = c2.selectbox("Avatar", K.AVATARS)
            code_in = st.text_input("O‘qituvchi kodi (faqat o‘qituvchilar uchun)", type="password") if teacher_code else ""
            go = st.form_submit_button("Hisob yaratish")
        if go:
            if not name.strip() or not username.strip() or len(password) < 8:
                st.error("Ism, login kiriting va kamida 8 belgili parol tanlang.")
            elif role == "teacher" and teacher_code and code_in != teacher_code:
                st.error("O‘qituvchi kodi noto‘g‘ri.")
            else:
                try:
                    K.create_user(username, password, name, role, avatar)
                    user = K.authenticate(username, password)
                    st.session_state["uid"] = user["id"]
                    flash("Hisob yaratildi. Xush kelibsiz!", "🎉")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


# ============================================================== Bosh sahifa
def quick_actions(items):
    cols = st.columns(len(items))
    for col, (label, target) in zip(cols, items):
        with col:
            btn(label, key=f"qa_{target}", on_click=goto, args=(target,))


def page_home():
    u = me()
    teacher = u["role"] == "teacher"
    lvl, into, size, title = K.level_info(u["xp"])
    st.markdown(f'<div class="hero"><div class="hero-av">{esc(u["avatar"] or "🦊")}</div><div>'
                f'<h1>Salom, {esc(u["name"])}!</h1><p>{esc(title)} · {lvl}-daraja · umumiy reyting: #{K.user_rank(u["id"])}</p></div></div>',
                unsafe_allow_html=True)
    st.progress(into / size, text=f"⭐ {into}/{size} XP — keyingi darajagacha {size - into} XP")
    done, streak = K.daily_status(u)
    a, b, c, d = st.columns(4)
    a.metric("⭐ XP", u["xp"])
    b.metric("🪙 Tangalar", u["coins"])
    c.metric("🏅 Daraja", lvl)
    d.metric("🔥 Kunlik seriya", f"{streak} kun")

    if teacher:
        with K.conn() as cn:
            n_cls = cn.execute("SELECT COUNT(*) FROM classes WHERE teacher=?", (u["id"],)).fetchone()[0]
            n_stu = cn.execute("""SELECT COUNT(DISTINCT m.student) FROM members m JOIN classes c ON c.id=m.class_id
                               WHERE c.teacher=?""", (u["id"],)).fetchone()[0]
            n_q = cn.execute("SELECT COUNT(*) FROM questions WHERE approved=1").fetchone()[0]
            n_pend = cn.execute("SELECT COUNT(*) FROM questions WHERE approved=0").fetchone()[0]
        a, b, c, d = st.columns(4)
        a.metric("🏫 Sinflarim", n_cls)
        b.metric("👥 O‘quvchilarim", n_stu)
        c.metric("📚 Savollar", n_q)
        d.metric("⏳ Tasdiq kutmoqda", n_pend)
        quick_actions([("⚡ Jonli xona", M_LIVE), ("🏫 Sinflar", T_PANEL), ("🤖 AI test", T_AI), ("➕ Savol", T_NEW), ("🕹️ O‘yinlar", M_GAMES)])
        hard = K.hardest_questions(5)
        if hard:
            st.subheader("📉 Eng qiyin savollar")
            table([{"Savol": h["question"], "Fan": h["subject"], "To‘g‘ri javob": f"{int(h['pct'])}%",
                    "Javoblar soni": h["shown"]} for h in hard])
        else:
            st.info("Savollar bo‘yicha statistika o‘quvchilar o‘ynaganidan keyin shu yerda paydo bo‘ladi.")
    else:
        if done:
            st.success(f"✅ Bugungi kunlik chaqiriq bajarildi: {done['correct']}/{done['total']} to‘g‘ri. Ertaga yangi savollar!")
        else:
            st.markdown('<div class="panel"><h3>🔥 Bugungi kunlik chaqiriq</h3><p>5 ta savol, bonus XP va tangalar. '
                        'Seriyani uzmang — har kun tanga bonusi oshadi!</p></div>', unsafe_allow_html=True)
        quick_actions([("🎮 Quiz", M_PLAY), ("🔥 Kunlik", M_DAILY), ("⚡ Jonli", M_LIVE), ("🕹️ 30 o‘yin", M_GAMES), ("🏆 Reyting", M_RANK)])
        hist = K.recent_results(u["id"], 15)
        if hist:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("📈 Aniqlik dinamikasi")
                df = pd.DataFrame({"Aniqlik %": [round(100 * r["correct"] / r["total"]) if r["total"] else 0 for r in hist]},
                                  index=range(1, len(hist) + 1))
                st.line_chart(df)
            with c2:
                st.subheader("🎯 Fanlar bo‘yicha")
                ss = K.subject_stats(u["id"])
                if ss:
                    st.bar_chart(pd.DataFrame({"To‘g‘ri %": [round(100 * s["c"] / s["t"]) for s in ss]},
                                              index=[s["subject"] for s in ss]))
        else:
            st.info("Birinchi quizni o‘ynang — statistika va grafiklar shu yerda paydo bo‘ladi.")
    tip = random.Random(date.today().isoformat()).choice(TIPS)
    st.markdown(f'<div class="panel"><b>💡 Kun maslahati</b><br>{esc(tip)}</div>', unsafe_allow_html=True)


# ============================================================== Quiz dvigateli
def quiz_start(pool, sec, mode):
    S = st.session_state
    qs = []
    for q in pool:
        q = dict(q)
        opts = list(q["options"])
        random.shuffle(opts)
        q["options"] = opts
        qs.append(q)
    S.update(quiz=qs, qi=0, score=0, correct=0, streak=0, best_streak=0, answered=False, selected=None,
             finished=False, qresults=[], time_per_q=sec, deadline=time.time() + sec, quiz_mode=mode,
             hidden=set(), used_time=False, finish_info=None, wrong_qs=[])


def quiz_reset():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v if not isinstance(v, list) else []


def register_answer(q, opt, left):
    S = st.session_state
    ok = opt is not None and opt == q["answer"]
    gained = 0
    S.selected, S.answered = opt, True
    if ok:
        S.streak += 1
        S.correct += 1
        S.best_streak = max(S.best_streak, S.streak)
        gained = 100 + min(S.streak - 1, 5) * 20 + left
        S.score += gained
    else:
        S.streak = 0
    S.qresults.append({"question": q["question"], "selected": opt if opt is not None else "Vaqt tugadi",
                       "answer": q["answer"], "correct": ok, "explanation": q.get("explanation", ""), "gained": gained})
    if S.quiz_mode != "practice" and q.get("id"):
        with K.conn() as c:
            K.record_stat(c, q["id"], ok)


def finish_quiz():
    S, u = st.session_state, me()
    qs, mode = S.quiz, S.quiz_mode
    S.wrong_qs = [q for q, r in zip(qs, S.qresults) if not r["correct"]]
    info = None
    if mode == "normal":
        subject = qs[0]["subject"] if len({q["subject"] for q in qs}) == 1 else "Aralash"
        info = K.complete_quiz(u["id"], subject, S.score, S.correct, len(qs), S.best_streak)
    elif mode == "daily":
        info = K.complete_daily(u["id"], S.score, S.correct, len(qs), S.best_streak)
    notify(info)
    S.finish_info, S.finished, S.deadline = info, True, None


def quiz_screen():
    S = st.session_state
    if S.finished:
        quiz_results()
    else:
        quiz_view()


def quiz_view():
    S, u = st.session_state, me()
    qs, i = S.quiz, S.qi
    q = qs[i]
    if not S.answered:
        st_autorefresh(interval=1000, key="quiz_tick")
    left_f = max(0.0, S.deadline - time.time()) if not S.answered else 0.0
    left = math.ceil(left_f)
    if not S.answered and left_f <= 0:
        register_answer(q, None, 0)
        st.rerun()
    labels = {"normal": "", "daily": "🔥 Kunlik chaqiriq", "practice": "🛠️ Mashq rejimi — XP berilmaydi"}
    if labels[S.quiz_mode]:
        st.caption(labels[S.quiz_mode])
    st.progress(i / len(qs), text=f"Savol {i + 1}/{len(qs)}")
    a, b, c = st.columns(3)
    a.metric("⭐ Ball", S.score)
    b.metric("🔥 Combo", S.streak)
    c.metric("⏱️ Vaqt", f"{left} s")
    if not S.answered:
        total = S.time_per_q + (10 if S.used_time else 0)
        st.progress(min(1.0, left_f / max(total, 1)))
    st.markdown(f'<div class="panel"><div class="qmeta">{esc(q["subject"])} · {esc(q["difficulty"])}</div>'
                f'<div class="qtext">{esc(q["question"])}</div></div>', unsafe_allow_html=True)

    if not S.answered:
        l1, l2 = st.columns(2)
        if l1.button("🌓 50/50 · 15 🪙", key=f"ll1_{i}", disabled=bool(S.hidden) or len(q["options"]) < 4):
            if K.spend(u["id"], 15):
                wrong = [o for o in q["options"] if o != q["answer"]]
                S.hidden = set(random.sample(wrong, 2))
            else:
                flash("Tangalar yetarli emas.", "⚠️")
            st.rerun()
        if l2.button("⏱️ +10 soniya · 10 🪙", key=f"ll2_{i}", disabled=S.used_time):
            if K.spend(u["id"], 10):
                S.deadline += 10
                S.used_time = True
            else:
                flash("Tangalar yetarli emas.", "⚠️")
            st.rerun()
        for j, opt in enumerate(q["options"]):
            if opt in (S.hidden or set()):
                continue
            if btn(f"{chr(65 + j)} · {opt}", key=f"qopt{j}_{i}"):
                register_answer(q, opt, left)
                st.rerun()
    else:
        last = S.qresults[-1]
        if last["correct"]:
            st.success(f"✅ To‘g‘ri! +{last['gained']} ball")
        elif S.selected is None:
            st.warning("⏰ Vaqt tugadi!")
        else:
            st.error("❌ Noto‘g‘ri javob")
        out = ""
        for j, opt in enumerate(q["options"]):
            cls, mark = "opt dim", ""
            if opt == q["answer"]:
                cls, mark = "opt ok", " ✅"
            elif opt == S.selected:
                cls, mark = "opt bad", " ❌"
            out += f'<div class="{cls}">{chr(65 + j)} · {esc(opt)}{mark}</div>'
        st.markdown(out, unsafe_allow_html=True)
        if q.get("explanation"):
            st.info("💡 " + q["explanation"])
        if btn("➡️ Keyingi savol" if i + 1 < len(qs) else "🏁 Natijani ko‘rish", key=f"next_{i}"):
            if i + 1 < len(qs):
                S.update(qi=i + 1, answered=False, selected=None, deadline=time.time() + S.time_per_q,
                         hidden=set(), used_time=False)
            else:
                finish_quiz()
            st.rerun()


def quiz_results():
    S = st.session_state
    qs, info = S.quiz, S.finish_info
    pct = round(100 * S.correct / len(qs))
    if pct >= 80:
        st.balloons()
    msg = ("🏆 Ajoyib natija!" if pct >= 80 else "👍 Yaxshi, davom eting!" if pct >= 50 else "💪 Mashq qiling — keyingi safar yaxshiroq bo‘ladi!")
    st.markdown(f'<div class="panel"><div class="qtext">{msg}</div></div>', unsafe_allow_html=True)
    a, b, c, d = st.columns(4)
    a.metric("⭐ Ball", S.score)
    b.metric("🎯 To‘g‘ri", f"{S.correct}/{len(qs)}")
    c.metric("📊 Aniqlik", f"{pct}%")
    d.metric("🔥 Eng uzun combo", S.best_streak)
    if info:
        st.success(f"Mukofot: +{info['xp']} XP · +{info['coins']} 🪙" + (f" · 🔥 {info['streak']} kunlik seriya" if info.get("streak") else ""))
    elif S.quiz_mode == "practice":
        st.caption("Mashq rejimida XP va tanga berilmaydi.")
    st.subheader("📋 Javoblar tahlili")
    for r in S.qresults:
        with st.expander(("✅ " if r["correct"] else "❌ ") + r["question"]):
            st.write(f"To‘g‘ri javob: **{r['answer']}**")
            if not r["correct"]:
                st.write(f"Sizning javobingiz: {r['selected']}")
            if r["explanation"]:
                st.caption(r["explanation"])
    c1, c2 = st.columns(2)
    if c1.button("🔁 Yangi o‘yin", key="again"):
        quiz_reset()
        st.rerun()
    if S.wrong_qs and c2.button(f"🛠️ Xatolarni qayta ishlash ({len(S.wrong_qs)})", key="practice"):
        quiz_start(S.wrong_qs, 30, "practice")
        st.rerun()


def page_play():
    S = st.session_state
    st.title("🎮 Quiz Arena")
    if S.quiz is not None:
        return quiz_screen()
    c1, c2 = st.columns(2)
    subject = c1.selectbox("Fan", ["Barcha fanlar"] + K.subjects(), key="pl_sub")
    diff = c2.selectbox("Qiyinlik", ["Barcha darajalar"] + K.DIFFS, key="pl_diff")
    pool = K.get_questions(sel_subject(subject), None if diff.startswith("Barcha") else diff)
    st.caption(f"📚 Mavjud savollar: {len(pool)}")
    if not pool:
        st.warning("Bu tanlovda savol topilmadi.")
        return
    count = count_slider("Savollar soni", len(pool), 5, 30, "pl_count")
    sec = st.select_slider("Har savol uchun vaqt (soniya)", options=[10, 15, 20, 30, 45, 60], value=15, key="pl_sec")
    st.caption("💡 Qiyin savolda 50/50 (15 🪙) yoki +10 soniya (10 🪙) yordamidan foydalanishingiz mumkin.")
    if st.button("🚀 O‘yinni boshlash", key="pl_start"):
        quiz_start(random.sample(pool, count), sec, "normal")
        st.rerun()


def page_daily():
    S, u = st.session_state, me()
    st.title("🔥 Kunlik chaqiriq")
    if S.quiz is not None:
        return quiz_screen()
    done, streak = K.daily_status(u)
    flames = "".join("🔥" if k < streak % 7 or (streak and streak % 7 == 0) else "▫️" for k in range(7))
    st.markdown(f'<div class="panel"><h3>Seriya: {streak} kun</h3><div style="font-size:1.8rem">{flames}</div>'
                f'<p class="small">Har kuni bir xil 5 ta savol hamma uchun. Bajarsangiz: XP, tangalar va seriya bonusi. '
                f'3 va 7 kunlik seriya uchun maxsus yutuqlar bor.</p></div>', unsafe_allow_html=True)
    if done:
        st.success(f"Bugun bajarildi: {done['correct']}/{done['total']} to‘g‘ri, {done['score']} ball. Ertaga yana keling!")
        return
    if st.button("🚀 Chaqiriqni boshlash (5 savol · 20 soniya)", key="daily_start"):
        qs = K.daily_questions()
        if not qs:
            st.error("Savollar topilmadi.")
        else:
            quiz_start(qs, 20, "daily")
            st.rerun()


# ============================================================== Uy vazifalari
def page_hw():
    u = me()
    st.title("📚 Mening uy vazifalarim")
    with K.conn() as c:
        classes = c.execute("SELECT classes.* FROM classes JOIN members ON members.class_id=classes.id WHERE members.student=?",
                            (u["id"],)).fetchall()
    if not classes:
        st.info("Hozircha sinfga qo‘shilmagansiz. «Sinfga qo‘shilish» bo‘limida kod kiriting.")
    for cl in classes:
        st.subheader("🏫 " + cl["name"])
        with K.conn() as c:
            assigns = c.execute("SELECT * FROM assignments WHERE class_id=? ORDER BY id DESC", (cl["id"],)).fetchall()
        if not assigns:
            st.caption("Hozircha vazifa yo‘q.")
        for ass in assigns:
            with K.conn() as c:
                done = c.execute("SELECT * FROM assignment_results WHERE assignment_id=? AND student=?", (ass["id"], u["id"])).fetchone()
            overdue = bool(ass["due"]) and K.today_str() > ass["due"]
            tag = "✅" if done else ("⚠️ muddati o‘tgan" if overdue else "📝")
            with st.expander(f"{tag} {ass['title']} · {ass['subject']} · muddat {ass['due'] or '—'}"):
                qs = json.loads(ass["questions"])
                if done:
                    st.success(f"Topshirilgan: {done['correct']}/{done['total']} to‘g‘ri" + (" (kechikib)" if done["late"] else ""))
                    for q in qs:
                        st.write(f"**{q['question']}**")
                        st.caption(f"To‘g‘ri javob: {q['answer']} · {q.get('explanation', '')}")
                    continue
                if overdue:
                    st.warning("Muddat o‘tgan: topshirsangiz, XP ikki baravar kam beriladi.")
                with st.form(f"homework_{ass['id']}"):
                    answers = [st.radio(f"{i + 1}. {q['question']}", q["options"], index=None, key=f"hw_{ass['id']}_{i}")
                               for i, q in enumerate(qs)]
                    submit = st.form_submit_button("✅ Vazifani topshirish")
                if submit:
                    if any(a is None for a in answers):
                        st.error("Barcha savollarga javob bering.")
                    else:
                        marks = [(q.get("id"), answers[i] == q["answer"]) for i, q in enumerate(qs)]
                        info = K.submit_assignment(ass["id"], u["id"], marks)
                        notify(info)
                        flash(f"Natija: {sum(ok for _, ok in marks)}/{len(qs)}", "📚")
                        st.rerun()


def page_join():
    u = me()
    st.title("🔑 Sinfga qo‘shilish")
    with st.form("join_class"):
        code = st.text_input("O‘qituvchi bergan 6 belgili kod", max_chars=6)
        go = st.form_submit_button("Sinfga qo‘shilish")
    if go:
        status, name = K.join_class(u["id"], code)
        if status == "none":
            st.error("Kod topilmadi. O‘qituvchidan tekshirib oling.")
        elif status == "again":
            st.info("Siz bu sinfga avval qo‘shilgansiz.")
        else:
            st.success(f"«{name}» sinfiga qo‘shildingiz.")
            st.balloons()


# ============================================================== O‘qituvchi paneli
def class_block(cl):
    cid = cl["id"]
    with K.conn() as c:
        members = c.execute("""SELECT users.id,users.name,users.username,users.xp,users.avatar FROM members
                            JOIN users ON users.id=members.student WHERE class_id=? ORDER BY users.xp DESC""", (cid,)).fetchall()
        assigns = c.execute("SELECT * FROM assignments WHERE class_id=? ORDER BY id DESC", (cid,)).fetchall()
    with st.expander(f"🏫 {cl['name']} · KOD: {cl['code']} · {len(members)} o‘quvchi"):
        t1, t2, t3, t4 = st.tabs(["👥 O‘quvchilar", "📝 Vazifa yaratish", "📈 Natijalar", "⚙️ Sozlamalar"])
        with t1:
            st.markdown(f'<div class="bigcode">{esc(cl["code"])}</div>', unsafe_allow_html=True)
            st.caption("Bu kodni o‘quvchilarga bering — ular «Sinfga qo‘shilish» bo‘limida kiritadi.")
            if members:
                table([{"": m["avatar"] or "", "Ism": m["name"], "Login": m["username"], "Daraja": K.level_info(m["xp"])[0],
                        "XP": m["xp"]} for m in members])
            else:
                st.caption("O‘quvchilar hali qo‘shilmagan.")
        with t2:
            subs = ["Barcha fanlar"] + K.subjects()
            sub = st.selectbox("Fan", subs, key=f"asub{cid}")
            pool = K.get_questions(sel_subject(sub))
            with st.form(f"assign_{cid}", clear_on_submit=True):
                title = st.text_input("Vazifa nomi")
                count = count_slider("Savollar soni", len(pool), 5, 20, f"acount{cid}")
                due = st.date_input("Topshirish sanasi", value=date.today() + timedelta(days=7))
                create = st.form_submit_button("Vazifani tayinlash")
            if create:
                if title.strip() and pool and count:
                    K.create_assignment(cid, title.strip(), sub, random.sample(pool, count), due)
                    flash("Vazifa tayinlandi!", "✅")
                    st.rerun()
                else:
                    st.error("Vazifa nomini kiriting va savollar mavjudligini tekshiring.")
        with t3:
            if not assigns:
                st.caption("Hali vazifa yo‘q.")
            for ass in assigns:
                with K.conn() as c:
                    marks = c.execute("""SELECT users.id uid,users.name,users.username,r.correct,r.total,r.submitted_at,r.late
                        FROM assignment_results r JOIN users ON users.id=r.student WHERE assignment_id=?
                        ORDER BY (1.0*r.correct/r.total) DESC, r.submitted_at""", (ass["id"],)).fetchall()
                st.markdown(f"#### {ass['title']} · {ass['subject']} · muddat {ass['due'] or '—'}")
                if marks:
                    avg = sum(m["correct"] / m["total"] for m in marks if m["total"]) / len(marks) * 100
                    a, b = st.columns(2)
                    a.metric("Topshirdi", f"{len(marks)}/{len(members)}")
                    b.metric("O‘rtacha natija", f"{avg:.0f}%")
                    rows = [{"O‘quvchi": m["name"], "Login": m["username"], "To‘g‘ri": f"{m['correct']}/{m['total']}",
                             "Vaqt": m["submitted_at"], "Kechikkan": "ha" if m["late"] else ""} for m in marks]
                    table(rows)
                    out = io.StringIO()
                    w = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
                    w.writeheader()
                    w.writerows(rows)
                    st.download_button("⬇️ CSV", out.getvalue(), f"{ass['title']}.csv", "text/csv", key=f"acsv{ass['id']}")
                else:
                    st.caption("Hali topshirilmagan.")
                submitted = {m["uid"] for m in marks}
                missing = [m["name"] for m in members if m["id"] not in submitted]
                if missing and members:
                    st.caption("Topshirmaganlar: " + ", ".join(missing))
                if st.button("🗑️ Vazifani o‘chirish", key=f"adel{ass['id']}"):
                    K.delete_assignment(ass["id"])
                    st.rerun()
                st.divider()
        with t4:
            st.warning("Sinfni o‘chirsangiz, uning vazifalari va natijalari ham o‘chadi.")
            sure = st.checkbox("Tushunaman, sinf o‘chirilsin", key=f"csure{cid}")
            if st.button("🗑️ Sinfni o‘chirish", key=f"cdel{cid}", disabled=not sure):
                K.delete_class(cid, me()["id"])
                st.rerun()


def page_panel():
    u = me()
    st.title("👩‍🏫 O‘qituvchi boshqaruv markazi")
    with st.form("class_form", clear_on_submit=True):
        cname = st.text_input("Yangi sinf nomi", placeholder="7-A / Informatika")
        make = st.form_submit_button("➕ Sinf yaratish")
    if make:
        if not cname.strip():
            st.error("Sinf nomini kiriting.")
        else:
            code = K.create_class(u["id"], cname.strip())
            st.success(f"Sinf yaratildi! O‘quvchilarga kodni bering: **{code}**")
    with K.conn() as c:
        classes = c.execute("SELECT * FROM classes WHERE teacher=? ORDER BY id DESC", (u["id"],)).fetchall()
    if not classes:
        st.info("Hozircha sinf yo‘q. Yuqoridagi forma orqali yarating.")
    for cl in classes:
        class_block(cl)


# ============================================================== Savollar banki
def page_bank():
    st.title("📝 Savollar banki")
    t1, t2 = st.tabs(["📚 Barcha savollar", "🛡️ Tasdiq kutayotganlar"])
    with t1:
        c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
        subject = c1.selectbox("Fan", ["Barcha fanlar"] + K.subjects(), key="bk_sub")
        diff = c2.selectbox("Daraja", ["Barcha darajalar"] + K.DIFFS, key="bk_diff")
        status = c3.selectbox("Holat", ["Hammasi", "Tasdiqlangan", "Kutayotgan"], key="bk_status")
        search = c4.text_input("🔎 Qidirish", key="bk_search")
        rows = K.get_questions(sel_subject(subject), None if diff.startswith("Barcha") else diff,
                               approved={"Hammasi": None, "Tasdiqlangan": True, "Kutayotgan": False}[status],
                               search=search.strip() or None)
        st.caption(f"Jami: {len(rows)} ta savol. Jadvalda to‘g‘ridan-to‘g‘ri tahrirlang, so‘ng «Saqlash» tugmasini bosing.")
        if rows:
            df = pd.DataFrame([{"ID": q["id"], "Fan": q["subject"], "Daraja": q["difficulty"], "Savol": q["question"],
                                "Tasdiq": bool(q["approved"]), "O‘chirish": False} for q in rows])
            edited = editor(df, hide_index=True, disabled=["ID"], key="bank_editor", num_rows="fixed",
                            column_config={"Daraja": st.column_config.SelectboxColumn(options=K.DIFFS, required=True),
                                           "Tasdiq": st.column_config.CheckboxColumn(),
                                           "O‘chirish": st.column_config.CheckboxColumn()})
            if st.button("💾 O‘zgarishlarni saqlash", key="bank_save"):
                orig = {q["id"]: q for q in rows}
                dels, changed = [], 0
                for _, r in edited.iterrows():
                    qid = int(r["ID"])
                    o = orig[qid]
                    if r["O‘chirish"]:
                        dels.append(qid)
                        continue
                    if (r["Fan"], r["Daraja"], r["Savol"]) != (o["subject"], o["difficulty"], o["question"]) \
                            and str(r["Savol"]).strip() and str(r["Fan"]).strip():
                        K.update_question(qid, r["Fan"], r["Daraja"], r["Savol"])
                        changed += 1
                    if bool(r["Tasdiq"]) != bool(o["approved"]):
                        K.approve_question(qid) if r["Tasdiq"] else K.set_unapproved(qid)
                        changed += 1
                if dels:
                    K.delete_questions(dels)
                flash(f"Saqlandi: {changed} ta o‘zgarish, {len(dels)} ta o‘chirildi.", "💾")
                st.rerun()
    with t2:
        pending = K.get_questions(approved=False)
        if not pending:
            st.caption("Tasdiq kutayotgan savol yo‘q.")
        else:
            if st.button(f"✅ Hammasini tasdiqlash ({len(pending)})", key="approve_all"):
                for q in pending:
                    K.approve_question(q["id"])
                st.rerun()
            for q in pending:
                with st.expander(f"{q['question']}  ·  {q['subject']}"):
                    for o in q["options"]:
                        st.write(("✅ " if o == q["answer"] else "• ") + o)
                    if q["explanation"]:
                        st.caption(q["explanation"])
                    a, b = st.columns(2)
                    if a.button("Tasdiqlash", key=f"approve{q['id']}"):
                        K.approve_question(q["id"])
                        st.rerun()
                    if b.button("Rad etish", key=f"reject{q['id']}"):
                        K.delete_questions([q["id"]])
                        st.rerun()


def question_form(teacher):
    u = me()
    existing = K.subjects()
    if existing:
        st.caption("Mavjud fanlar: " + ", ".join(existing))
    with st.form("question_form", clear_on_submit=True):
        subject = st.text_input("Fan / mavzu", "Informatika")
        diff = st.selectbox("Qiyinlik", K.DIFFS)
        question = st.text_area("Savol matni")
        opts = [st.text_input(f"{chr(65 + i)} varianti", key=f"newq_opt{i}") for i in range(4)]
        ai = st.selectbox("To‘g‘ri javob", range(4), format_func=lambda i: f"{chr(65 + i)} varianti")
        explanation = st.text_area("Javob izohi (ixtiyoriy)")
        submit = st.form_submit_button("Saqlash")
    if submit:
        opts = [o.strip() for o in opts]
        err = K.validate_question(question, opts, opts[ai])
        if err:
            st.error(err)
        elif K.question_exists(question):
            st.error("Bunday savol bankda allaqachon bor.")
        else:
            K.add_question(u["id"], subject.strip() or "Umumiy", diff, question.strip(), opts, opts[ai],
                           explanation.strip(), 1 if teacher else 0)
            st.success("Savol qo‘shildi." if teacher else "Savol o‘qituvchi ko‘rib chiqishi uchun yuborildi. Tasdiqlansa, bonus olasiz!")


def page_new():
    st.title("➕ Savol yaratish")
    question_form(True)


def page_suggest():
    st.title("💡 Savol taklif qilish")
    st.caption("Taklif qilgan savolingiz o‘qituvchi tomonidan tasdiqlansa, +30 XP, +10 🪙 va «Hissa qo‘shuvchi» yutug‘i beriladi.")
    question_form(False)
    mine = K.my_suggestions(me()["id"])
    if mine:
        st.subheader("📨 Mening takliflarim")
        table([{"Savol": m["question"], "Fan": m["subject"], "Holat": "✅ Tasdiqlangan" if m["approved"] else "⏳ Kutilmoqda"} for m in mine])


# ============================================================== AI yordamchi
def page_ai():
    u = me()
    st.title("🤖 AI test yordamchisi")
    st.markdown('<div class="panel"><h3>Haqiqiy AI yordamida test yarating</h3><p>Mavzu, daraja va savollar sonini tanlang. '
                'Natijani tekshirib, kerakli savollarni tanlab bankka saqlang.</p></div>', unsafe_allow_html=True)
    api_key = secret("OPENAI_API_KEY")
    if api_key:
        st.success("🔑 OpenAI kaliti server sozlamalaridan ulangan.")
    else:
        api_key = st.text_input("OpenAI API kaliti", type="password", help="Kalit faqat shu sessiyada ishlatiladi va saqlanmaydi.")
        st.caption("Kalit bo‘lmasa ham, platformaning boshqa funksiyalari ishlayveradi.")
    with st.form("ai_builder"):
        topic = st.text_input("Mavzu", placeholder="Masalan: Python’da sikllar")
        c1, c2 = st.columns(2)
        count = c1.slider("Nechta savol?", 1, 20, 5)
        level = c2.selectbox("Qiyinlik", K.DIFFS)
        grade = c1.selectbox("Sinf / daraja", ["Boshlang‘ich", "5–7-sinf", "8–9-sinf", "10–11-sinf", "Talabalar / kattalar"])
        language = c2.selectbox("Savollar tili", ["O‘zbek tili", "Русский язык", "English"])
        model = st.text_input("Model", value=secret("OPENAI_MODEL", "gpt-4o-mini"))
        generate = st.form_submit_button("✨ AI orqali savollar yaratish")
    if generate:
        if not topic.strip():
            st.error("Mavzu kiriting.")
        elif not api_key.strip():
            st.error("AI ishlashi uchun OpenAI API kalitini kiriting.")
        else:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key.strip())
                prompt = f"""Create exactly {count} high-quality multiple-choice quiz questions in {language} about: {topic.strip()}.
Audience: {grade}. Difficulty: {level}. Return ONLY valid JSON, no markdown, with this schema:
{{"questions":[{{"question":"...","options":["A","B","C","D"],"answer":"exactly one option text","explanation":"brief explanation"}}]}}
Requirements: factual, distinct questions; exactly 4 plausible but different options per question; answer must exactly match one option; explanation in the requested language; do not invent facts; avoid repeated questions."""
                with st.spinner("AI savollar tayyorlamoqda..."):
                    response = client.chat.completions.create(
                        model=model.strip() or "gpt-4o-mini",
                        messages=[{"role": "system", "content": "You create accurate educational multiple-choice questions. Follow the requested JSON schema exactly."},
                                  {"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}, temperature=0.4)
                raw = (response.choices[0].message.content or "{}").strip()
                raw = re.sub(r"^```(?:json)?|```$", "", raw).strip()
                items = json.loads(raw).get("questions", [])
                draft = []
                for it in items:
                    q, err = K.normalize_question({**it, "subject": topic.strip(), "difficulty": level})
                    if q:
                        draft.append(q)
                if len(draft) != count:
                    st.warning(f"{count} ta so‘ralgan savoldan {len(draft)} tasi tekshiruvdan o‘tdi.")
                if draft:
                    st.session_state["ai_draft"] = draft
                    st.success(f"{len(draft)} ta savol yaratildi. Saqlashdan oldin tekshiring.")
                else:
                    st.error("AI javobi kerakli formatda kelmadi. Qayta urinib ko‘ring.")
            except ImportError:
                st.error("OpenAI kutubxonasi topilmadi: python -m pip install -r requirements.txt")
            except Exception as e:
                st.error(f"AI so‘rovida xato: {e}")
    draft = st.session_state.get("ai_draft")
    if draft:
        st.subheader("🧪 Yaratilgan savollarni tekshirish")
        st.warning("AI xato qilishi mumkin — darsda ishlatishdan oldin mazmunan tekshiring. Keraksizlarining belgisini olib tashlang.")
        for i, q in enumerate(draft):
            keep = st.checkbox(f"{i + 1}. {q['question']}", value=True, key=f"aikeep{i}")
            with st.container():
                for o in q["options"]:
                    st.caption(("✅ " if o == q["answer"] else "• ") + o)
                if q["explanation"]:
                    st.caption("💡 " + q["explanation"])
            q["_keep"] = keep
        c1, c2 = st.columns(2)
        if c1.button("💾 Tanlanganlarni bankka saqlash", key="ai_save"):
            saved = 0
            for q in draft:
                if q.get("_keep") and not K.question_exists(q["question"]):
                    K.add_question(u["id"], q["subject"], q["difficulty"], q["question"], q["options"], q["answer"], q["explanation"], 1)
                    saved += 1
            st.session_state["ai_draft"] = []
            flash(f"{saved} ta savol bankka saqlandi.", "💾")
            st.rerun()
        if c2.button("🗑️ Bekor qilish", key="ai_cancel"):
            st.session_state["ai_draft"] = []
            st.rerun()


# ============================================================== Import / eksport
def page_io():
    u = me()
    st.title("📂 Savollar importi va eksporti")
    st.caption("Qo‘llab-quvvatlanadi: JSON ({\"questions\": [...]}) va CSV. Variantlar: ro‘yxat yoki «A|B|C|D»; javob: matn yoki A–D harfi.")
    uploaded = st.file_uploader("JSON yoki CSV faylni tanlang", type=["json", "csv"])
    if uploaded:
        try:
            if uploaded.name.lower().endswith(".json"):
                data = json.loads(uploaded.getvalue().decode("utf-8-sig"))
                data = data.get("questions", []) if isinstance(data, dict) else data
            else:
                data = list(csv.DictReader(io.StringIO(uploaded.getvalue().decode("utf-8-sig"))))
            good, bad, dup = [], 0, 0
            for raw in data:
                q, err = K.normalize_question(raw) if isinstance(raw, dict) else (None, "format")
                if not q:
                    bad += 1
                elif K.question_exists(q["question"]):
                    dup += 1
                else:
                    good.append(q)
            a, b, c = st.columns(3)
            a.metric("✅ Yaroqli", len(good))
            b.metric("♻️ Takroriy", dup)
            c.metric("❌ Xato", bad)
            if good:
                table([{"Fan": q["subject"], "Daraja": q["difficulty"], "Savol": q["question"], "Javob": q["answer"]} for q in good[:50]])
                if st.button(f"📥 {len(good)} ta savolni import qilish", key="do_import"):
                    for q in good:
                        K.add_question(u["id"], q["subject"], q["difficulty"], q["question"], q["options"], q["answer"], q["explanation"], 1)
                    flash(f"{len(good)} ta savol import qilindi.", "📥")
                    st.rerun()
        except Exception as e:
            st.error(f"Faylni o‘qishda xato: {e}")
    st.divider()
    st.subheader("⬇️ Eksport")
    qs = K.get_questions(approved=None)
    export = [{k: q[k] for k in ["subject", "difficulty", "question", "options", "answer", "explanation"]} for q in qs]
    c1, c2, c3 = st.columns(3)
    c1.download_button("⬇️ JSON", json.dumps({"questions": export}, ensure_ascii=False, indent=2), "quiz_questions.json", "application/json")
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=["subject", "difficulty", "question", "options", "answer", "explanation"])
    w.writeheader()
    for q in export:
        w.writerow({**q, "options": json.dumps(q["options"], ensure_ascii=False)})
    c2.download_button("⬇️ CSV", out.getvalue(), "quiz_questions.csv", "text/csv")
    sample = {"questions": [{"subject": "Informatika", "difficulty": "Oson", "question": "1 kilobayt necha bayt?",
                             "options": ["100", "1000", "1024", "512"], "answer": "1024", "explanation": "1 KB = 1024 bayt."}]}
    c3.download_button("📄 Namuna fayl", json.dumps(sample, ensure_ascii=False, indent=2), "namuna.json", "application/json")


# ============================================================== Jonli viktorina
def tiles(q, reveal=False):
    out = ""
    for j, opt in enumerate(q["options"]):
        style, mark = f"background:{OPT_COLORS[j % 4]}", ""
        if reveal:
            if opt == q["answer"]:
                mark = " ✅"
            else:
                style += ";opacity:.3"
        out += f'<div class="tile" style="{style}"><span>{OPT_SHAPES[j % 4]}</span><span>{esc(opt)}{mark}</span></div>'
    return f'<div class="tiles">{out}</div>'


def chips(board):
    return "".join(f'<span class="chip">{esc(p["avatar"] or "🙂")} {esc(p["name"])}</span>' for p in board)


def board_rows(board, n=None):
    return [{"O‘rin": i + 1, "Ism": f"{p['avatar'] or ''} {p['name']}", "Ball": p["points"], "To‘g‘ri": p["correct_count"]}
            for i, p in enumerate(board[:n] if n else board)]


def host_panel(rid):
    u = me()
    room = K.get_room(rid)
    if not room:
        return
    qs = json.loads(room["questions"])
    phase = K.effective_phase(room)
    if room["status"] == "live" and phase == "reveal" and room["phase"] != "reveal":
        K.set_phase(rid, "reveal")
    st.markdown(f'<div class="bigcode">{esc(room["code"])}</div>', unsafe_allow_html=True)
    board = K.room_scoreboard(rid)
    if room["status"] == "lobby":
        st.caption("O‘quvchilar «⚡ Jonli viktorina» bo‘limida shu kod bilan kiradi.")
        st.markdown(chips(board) if board else "⏳ O‘yinchilar kutilmoqda...", unsafe_allow_html=True)
        st.write(f"👥 Qo‘shilganlar: **{len(board)}** · Savollar: {len(qs)} · Har savolga {room['q_limit']} soniya")
        if st.button("▶️ O‘yinni boshlash", key=f"lvs{rid}", disabled=not board):
            K.start_room(rid, u["id"])
            st.rerun()
    elif room["status"] == "live":
        qi = room["current_q"]
        q = qs[qi]
        st.progress((qi + 1) / len(qs), text=f"Savol {qi + 1}/{len(qs)}")
        st.markdown(f'<div class="panel"><div class="qtext">{esc(q["question"])}</div></div>', unsafe_allow_html=True)
        answered, players = K.answer_count(rid, qi)
        if phase == "question":
            left = K.time_left(room)
            st.progress(min(1.0, left / max(room["q_limit"], 1)), text=f"⏱️ {math.ceil(left)} s · javob berdi: {answered}/{players}")
            st.markdown(tiles(q), unsafe_allow_html=True)
            if st.button("⏭ Javobni ko‘rsatish", key=f"lvr{rid}_{qi}"):
                K.set_phase(rid, "reveal")
                st.rerun()
        else:
            st.markdown(tiles(q, True), unsafe_allow_html=True)
            dist = K.answer_distribution(rid, qi)
            st.bar_chart(pd.DataFrame({"Javoblar": [dist.get(o, 0) for o in q["options"]]},
                                      index=[f"{OPT_SHAPES[j]} {o}" for j, o in enumerate(q["options"])]))
            if q.get("explanation"):
                st.info("💡 " + q["explanation"])
            st.markdown("**🏆 Hozirgi TOP-5**")
            table(board_rows(board, 5))
            last = qi + 1 >= len(qs)
            if st.button("🏁 Yakunlash" if last else "➡️ Keyingi savol", key=f"lvn{rid}_{qi}"):
                K.advance_room(rid, u["id"])
                st.rerun()
        if st.button("⛔ Erta yakunlash", key=f"lvf{rid}"):
            K.finish_room(rid, u["id"])
            st.rerun()
    else:
        st.success("🏁 Viktorina yakunlandi. Podium bonuslari berildi (1-o‘rin +100 XP, 2-o‘rin +60, 3-o‘rin +30).")
        podium(board)
        table(board_rows(board))
        if board:
            out = io.StringIO()
            w = csv.DictWriter(out, fieldnames=list(board_rows(board)[0].keys()))
            w.writeheader()
            w.writerows(board_rows(board))
            st.download_button("⬇️ Natijalar (CSV)", out.getvalue(), f"{room['code']}_natijalar.csv", "text/csv", key=f"lvcsv{rid}")
    if room["status"] != "live" and st.button("🗑️ Xonani o‘chirish", key=f"lvd{rid}"):
        K.delete_room(rid, u["id"])
        st.rerun()


def live_host():
    u = me()
    rooms = K.host_rooms(u["id"])
    with st.expander("➕ Yangi xona yaratish", expanded=not rooms):
        title = st.text_input("Viktorina nomi", "Sinf bilan jonli quiz", key="lv_title")
        subj = st.selectbox("Fan", ["Barcha fanlar"] + K.subjects(), key="lv_subj")
        pool = K.get_questions(sel_subject(subj))
        count = count_slider("Savollar soni", len(pool), 10, 30, "lv_count")
        sec = st.select_slider("Har savol uchun vaqt (soniya)", options=[10, 15, 20, 30, 45, 60], value=20, key="lv_sec")
        if st.button("🚀 Xona yaratish", key="lv_create"):
            if not pool or not title.strip():
                st.error("Viktorina nomi va savollar kerak.")
            else:
                code = K.create_room(u["id"], title.strip(), random.sample(pool, count), sec)
                flash(f"Xona yaratildi! Kod: {code}", "🎮")
                st.rerun()
    icons = {"lobby": "🟡 kutish", "live": "🟢 jonli", "finished": "🏁 tugagan"}
    first_open = True
    for room in rooms:
        is_open = room["status"] != "finished" and first_open
        first_open = first_open and not is_open
        with st.expander(f"{icons[room['status']]} · {room['title']} · {room['code']}", expanded=is_open):
            host_panel(room["id"])


def live_player():
    u, S = me(), st.session_state
    rid = S.get("live_room_id")
    room = K.get_room(rid) if rid else None
    if not room:
        S["live_room_id"] = None
        with st.form("live_join_form"):
            code = st.text_input("O‘qituvchi bergan xona kodi", max_chars=6, placeholder="ABC123")
            go = st.form_submit_button("🎟️ Xonaga kirish")
        if go:
            status, r = K.join_room(code, u["id"])
            if status == "none":
                st.error("Bu kod bilan xona topilmadi.")
            elif status == "finished":
                st.error("Bu viktorina allaqachon yakunlangan.")
            else:
                S["live_room_id"] = r["id"]
                flash(f"«{r['title']}» xonasiga kirdingiz.", "🎮")
                st.rerun()
        return
    qs = json.loads(room["questions"])
    board = K.room_scoreboard(rid)
    c1, c2 = st.columns([4, 1])
    c1.markdown(f'<div class="panel"><h3>🎮 {esc(room["title"])}</h3><span class="small">Xona kodi: {esc(room["code"])} · '
                f'o‘yinchilar: {len(board)}</span></div>', unsafe_allow_html=True)
    if c2.button("🚪 Chiqish", key="lv_leave"):
        S["live_room_id"] = None
        st.rerun()
    rank = next((i + 1 for i, p in enumerate(board) if p["user_id"] == u["id"]), None)
    mine_pts = next((p["points"] for p in board if p["user_id"] == u["id"]), 0)
    if room["status"] == "lobby":
        st.info("O‘qituvchi o‘yinni boshlashini kuting. Sahifa o‘zi yangilanadi.")
        st.markdown(chips(board), unsafe_allow_html=True)
    elif room["status"] == "finished":
        st.balloons()
        st.success(f"🏁 O‘yin tugadi! Sizning o‘rningiz: #{rank} · {mine_pts} ball" if rank else "🏁 O‘yin tugadi!")
        podium(board)
        table(board_rows(board))
    else:
        qi = room["current_q"]
        q = qs[qi]
        phase = K.effective_phase(room)
        st.progress((qi + 1) / len(qs), text=f"Savol {qi + 1}/{len(qs)} · sizning ballingiz: {mine_pts}" + (f" · #{rank}" if rank else ""))
        st.markdown(f'<div class="panel"><div class="qtext">{esc(q["question"])}</div></div>', unsafe_allow_html=True)
        mine = K.my_live_answer(rid, u["id"], qi)
        if phase == "question":
            left = K.time_left(room)
            st.progress(min(1.0, left / max(room["q_limit"], 1)), text=f"⏱️ {math.ceil(left)} s")
            if mine:
                st.success("Javobingiz qabul qilindi! Boshqalarni kutamiz...")
            else:
                cols = st.columns(2)
                for j, opt in enumerate(q["options"]):
                    with cols[j % 2]:
                        if btn(f"{OPT_SHAPES[j % 4]}  {opt}", key=f"lva{j}_{rid}_{qi}"):
                            res = K.submit_live_answer(rid, u["id"], opt)
                            if res.get("error") == "late":
                                flash("Vaqt tugagan edi.", "⏰")
                            elif res.get("error"):
                                flash("Javob qabul qilinmadi.", "⚠️")
                            else:
                                notify(res)
                            st.rerun()
        else:
            st.markdown(tiles(q, True), unsafe_allow_html=True)
            if mine and mine["correct"]:
                st.success(f"✅ To‘g‘ri! +{mine['points']} ball")
            elif mine:
                st.error("❌ Noto‘g‘ri javob")
            else:
                st.warning("⏰ Javob bermadingiz")
            if q.get("explanation"):
                st.info("💡 " + q["explanation"])
            st.markdown("**🏆 TOP-5**")
            table(board_rows(board, 5))
            st.caption("O‘qituvchi keyingi savolga o‘tishini kuting...")


def page_live():
    u, S = me(), st.session_state
    teacher = u["role"] == "teacher"
    active = teacher and any(r["status"] != "finished" for r in K.host_rooms(u["id"]))
    rid = S.get("live_room_id")
    if rid:
        room = K.get_room(rid)
        if room and room["status"] != "finished":
            active = True
    if active:
        st_autorefresh(interval=2000, key="live_tick")
    st.title("⚡ Jonli viktorina")
    if teacher:
        t1, t2 = st.tabs(["🎤 Boshqaruv", "🎟️ O‘yinchi sifatida"])
        with t1:
            live_host()
        with t2:
            live_player()
    else:
        st.caption("Kodni o‘qituvchidan oling, xonaga kiring va bir vaqtda raqobatlashing. Tezroq javob — ko‘proq ball!")
        live_player()


# ============================================================== Reyting
def page_rank():
    u = me()
    st.title("🏆 Reyting")
    st.caption(f"Sizning umumiy o‘rningiz: #{K.user_rank(u['id'])}")
    t1, t2, t3 = st.tabs(["⭐ XP bo‘yicha", "📅 Haftalik ball", "🎯 Eng yaxshi o‘yinlar"])
    with t1:
        top = K.top_xp(20)
        podium([{"name": r["name"], "points": r["xp"], "avatar": r["avatar"]} for r in top[:3]], unit="XP")
        table([{"O‘rin": i + 1, "Ism": f"{r['avatar'] or ''} {r['name']}", "Rol": "O‘qituvchi" if r["role"] == "teacher" else "O‘quvchi",
                "Daraja": K.level_info(r["xp"])[0], "XP": r["xp"], "Tangalar": r["coins"]} for i, r in enumerate(top)])
    with t2:
        wk = K.weekly_board(20)
        if wk:
            podium([{"name": r["name"], "points": r["pts"], "avatar": r["avatar"]} for r in wk[:3]])
            table([{"O‘rin": i + 1, "Ism": f"{r['avatar'] or ''} {r['name']}", "Ball": r["pts"], "O‘yinlar": r["games"]} for i, r in enumerate(wk)])
        else:
            st.info("So‘nggi 7 kunda o‘yinlar yo‘q. Birinchi bo‘ling!")
    with t3:
        bg = K.best_games(20)
        if bg:
            table([{"O‘rin": i + 1, "Ism": f"{r['avatar'] or ''} {r['name']}", "Ball": r["score"], "To‘g‘ri": f"{r['correct']}/{r['total']}",
                    "Fan": r["subject"], "Sana": r["played_at"]} for i, r in enumerate(bg)])
        else:
            st.info("Hali o‘yin natijalari yo‘q.")


# ============================================================== Profil
def page_profile():
    u = me()
    lvl, into, size, title = K.level_info(u["xp"])
    st.title("👤 Profil va dizayn")
    st.markdown(f'<div class="hero"><div class="hero-av">{esc(u["avatar"] or "🦊")}</div><div><h1>{esc(u["name"])}</h1>'
                f'<p>@{esc(u["username"])} · {esc(title)} · {lvl}-daraja</p></div></div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📊 Statistika", "🎖️ Yutuqlar", "⚙️ Sozlamalar va dizayn"])
    with t1:
        hist = K.recent_results(u["id"], 30)
        if not hist:
            st.info("Hali o‘yin natijalari yo‘q.")
        else:
            tot_c, tot_t = sum(r["correct"] for r in hist), sum(r["total"] for r in hist)
            a, b, c = st.columns(3)
            a.metric("🎮 O‘yinlar (so‘nggi 30)", len(hist))
            b.metric("📊 O‘rtacha aniqlik", f"{round(100 * tot_c / tot_t) if tot_t else 0}%")
            c.metric("🏅 Eng yuqori ball", max(r["score"] for r in hist))
            st.line_chart(pd.DataFrame({"Ball": [r["score"] for r in hist]}, index=range(1, len(hist) + 1)))
            ss = K.subject_stats(u["id"])
            if ss:
                st.bar_chart(pd.DataFrame({"To‘g‘ri %": [round(100 * s["c"] / s["t"]) for s in ss]}, index=[s["subject"] for s in ss]))
            table([{"Sana": r["played_at"], "Fan": r["subject"], "Ball": r["score"], "To‘g‘ri": f"{r['correct']}/{r['total']}"} for r in reversed(hist[-10:])])
    with t2:
        got = K.earned_badges(u["id"])
        st.caption(f"Ochilgan yutuqlar: {len(got)}/{len(K.BADGES)}")
        cols = st.columns(3)
        for i, (key, (icon, name, desc)) in enumerate(K.BADGES.items()):
            earned = key in got
            cols[i % 3].markdown(f'<div class="badge {"" if earned else "locked"}"><b>{icon} {esc(name)}</b>'
                                 f'<span>{esc(desc)}{" · " + got[key][:10] if earned else " 🔒"}</span></div>', unsafe_allow_html=True)
    with t3:
        with st.form("profile_form"):
            name = st.text_input("Ism-familiya", value=u["name"])
            avatar = st.selectbox("Avatar", K.AVATARS, index=K.AVATARS.index(u["avatar"]) if u["avatar"] in K.AVATARS else 0)
            keys = list(THEMES)
            theme = st.radio("Dizayn mavzusi", keys, index=keys.index(u["theme"]) if u["theme"] in keys else 0,
                             format_func=lambda k: THEMES[k]["label"], horizontal=True)
            save = st.form_submit_button("💾 Saqlash")
        if save:
            if not name.strip():
                st.error("Ism bo‘sh bo‘lmasligi kerak.")
            else:
                K.update_profile(u["id"], name, avatar, theme)
                flash("Profil yangilandi.", "✅")
                st.rerun()
        st.subheader("🔒 Parolni almashtirish")
        with st.form("pw_form", clear_on_submit=True):
            old = st.text_input("Joriy parol", type="password")
            new = st.text_input("Yangi parol (kamida 8 belgi)", type="password")
            go = st.form_submit_button("Almashtirish")
        if go:
            if len(new) < 8:
                st.error("Yangi parol kamida 8 belgidan iborat bo‘lsin.")
            elif K.change_password(u["id"], old, new):
                st.success("Parol almashtirildi.")
            else:
                st.error("Joriy parol noto‘g‘ri.")


# ============================================================== Musiqa va fokus
POMODORO = """
<div style="font-family:Inter,system-ui,sans-serif;text-align:center;color:#fff;background:linear-gradient(135deg,#252853,#191a37);
  border:1px solid #4b4780;border-radius:18px;padding:18px">
  <div id="mode" style="opacity:.85;font-weight:600">🎯 Fokus vaqti</div>
  <div id="t" style="font-size:56px;font-weight:800;margin:6px 0;font-variant-numeric:tabular-nums">25:00</div>
  <button onclick="startT()" style="padding:8px 16px;border:0;border-radius:10px;background:#6847ff;color:#fff;font-weight:700;cursor:pointer">▶️ Boshlash</button>
  <button onclick="pauseT()" style="padding:8px 16px;border:0;border-radius:10px;background:#444a7a;color:#fff;font-weight:700;cursor:pointer">⏸ To‘xtatish</button>
  <button onclick="resetT()" style="padding:8px 16px;border:0;border-radius:10px;background:#444a7a;color:#fff;font-weight:700;cursor:pointer">↺ Qayta</button>
</div>
<script>
let focus=true,left=25*60,timer=null;
function fmt(){const m=String(Math.floor(left/60)).padStart(2,'0'),s=String(left%60).padStart(2,'0');document.getElementById('t').textContent=m+':'+s;
  document.getElementById('mode').textContent=focus?'🎯 Fokus vaqti':'☕ Dam olish';}
function beep(){try{const a=new (window.AudioContext||window.webkitAudioContext)(),o=a.createOscillator();o.connect(a.destination);o.frequency.value=880;o.start();setTimeout(()=>o.stop(),400);}catch(e){}}
function tick(){left--;if(left<=0){beep();focus=!focus;left=(focus?25:5)*60;}fmt();}
function startT(){if(!timer)timer=setInterval(tick,1000);}
function pauseT(){clearInterval(timer);timer=null;}
function resetT(){pauseT();focus=true;left=25*60;fmt();}
fmt();
</script>
"""


def page_music():
    st.title("🎵 Musiqa va fokus")
    st.markdown('<div class="panel"><h3>🎧 O‘qish uchun muhit</h3><p>Fokus taymeri, o‘zingizning audio faylingiz yoki YouTube musiqasi.</p></div>', unsafe_allow_html=True)
    st.subheader("⏳ Pomodoro taymeri")
    try:
        import streamlit.components.v1 as components
        components.html(POMODORO, height=210)
    except Exception:
        st.caption("Taymerni ko‘rsatib bo‘lmadi.")
    st.subheader("💿 Audio fayl")
    audio = st.file_uploader("MP3, WAV, OGG yoki M4A fayl yuklang", type=["mp3", "wav", "ogg", "m4a"])
    if audio is not None:
        st.audio(audio.getvalue(), format=audio.type or "audio/mpeg")
    else:
        st.info("Audio fayl brauzerda ijro etiladi va serverga doimiy saqlanmaydi.")
    st.subheader("▶️ YouTube musiqasi")
    yt = st.text_input("YouTube video havolasi", placeholder="https://www.youtube.com/watch?v=...")
    if yt.strip():
        m = re.search(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([A-Za-z0-9_-]{11})", yt.strip())
        if m:
            st.video("https://www.youtube.com/watch?v=" + m.group(1))
        else:
            st.warning("YouTube havolasi noto‘g‘ri ko‘rinadi.")
    st.caption("Eslatma: boshqa sahifaga o‘tganda musiqa to‘xtashi mumkin.")


# ============================================================== Asosiy oqim
PAGES = {
    M_HOME: page_home, M_PLAY: page_play, M_DAILY: page_daily, M_LIVE: page_live, M_HW: page_hw, M_JOIN: page_join,
    M_GAMES: games.page_games, M_SUGGEST: page_suggest, M_RANK: page_rank, M_MUSIC: page_music, M_PROFILE: page_profile,
    T_PANEL: page_panel, T_BANK: page_bank, T_NEW: page_new, T_AI: page_ai, T_IO: page_io,
}
MENU_STUDENT = [M_HOME, M_PLAY, M_DAILY, M_LIVE, M_GAMES, M_HW, M_JOIN, M_SUGGEST, M_RANK, M_MUSIC, M_PROFILE]
MENU_TEACHER = [M_HOME, T_PANEL, T_BANK, T_NEW, T_AI, T_IO, M_LIVE, M_GAMES, M_RANK, M_MUSIC, M_PROFILE]


def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]


def main():
    st.set_page_config(page_title="Quiz Arena PRO", page_icon="🎮", layout="wide", initial_sidebar_state="expanded")
    boot()
    S = st.session_state
    for k, v in DEFAULTS.items():
        if k not in S:
            S[k] = [] if isinstance(v, list) else v
    user = K.get_user_by_id(S["uid"]) if S.get("uid") else None
    inject_css(user["theme"] if user else "neon")
    if not user:
        S.pop("uid", None)
        login_screen()
        show_flash()
        return
    S["_me"] = user
    teacher = user["role"] == "teacher"
    menu = MENU_TEACHER if teacher else MENU_STUDENT
    if S.get("nav") not in menu:
        S["nav"] = menu[0]
    lvl, into, size, title = K.level_info(user["xp"])
    with st.sidebar:
        st.markdown(f'<div class="side-user"><div class="av">{esc(user["avatar"] or "🦊")}</div><div><b>{esc(user["name"])}</b><br>'
                    f'<span class="small">{"👩‍🏫 O‘qituvchi" if teacher else "🎓 O‘quvchi"} · {esc(title)}</span></div></div>', unsafe_allow_html=True)
        st.progress(into / size, text=f"{lvl}-daraja · {into}/{size} XP")
        a, b = st.columns(2)
        a.metric("⭐ XP", user["xp"])
        b.metric("🪙 Tanga", user["coins"])
        st.radio("MENYU", menu, key="nav", label_visibility="collapsed")
        st.divider()
        if st.button("🚪 Chiqish", key="logout_btn"):
            logout()
            st.rerun()
    show_flash()
    games.setup(me=me, notify=notify, btn=btn, table=table)
    PAGES[S["nav"]]()
    st.caption("Quiz Arena PRO 2.0 · Streamlit + SQLite · AI savollar uchun OpenAI API kaliti kerak.")


if __name__ == "__main__":
    main()
