"""Quiz Arena PRO — 30 ta mini-o‘yin va «O‘yinlar markazi»."""
import html
import math
import random
import time

import streamlit as st

import core as K

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    def st_autorefresh(*a, **k):
        return 0

esc = html.escape
H = {}


def setup(**kw):
    """app.py dan yordamchi funksiyalarni ulaydi: me, notify, btn, table."""
    H.update(kw)


def me():
    return H["me"]()


# ============================================================== Holat va umumiy qismlar
def G():
    return st.session_state.setdefault("gm_state", {})


def start(key):
    st.session_state["gm_active"] = key
    st.session_state["gm_state"] = {}


def leave():
    st.session_state["gm_active"] = None
    st.session_state["gm_state"] = {}


def end_screen(key, score, perf, stats, note=None):
    """Yakuniy ekran. Mukofot faqat bir marta beriladi."""
    g = G()
    if g.get("rewarded") is None:
        g["rewarded"] = K.complete_game(me()["id"], key, int(score), perf)
        H["notify"](g["rewarded"])
    info = g["rewarded"]
    if perf >= 0.8:
        st.balloons()
    st.markdown(f'<div class="panel"><div class="qtext">🏁 O‘yin tugadi!</div>'
                f'<div class="qmeta">{esc(note or "")}</div></div>', unsafe_allow_html=True)
    cols = st.columns(len(stats) + 1)
    cols[0].metric("⭐ Ball", int(score))
    for col, (label, val) in zip(cols[1:], stats):
        col.metric(label, val)
    if info["capped"]:
        st.info("Bugungi mini-o‘yin XP limiti to‘ldi. Natija rekordga yoziladi, lekin XP berilmaydi. Ertaga davom eting!")
    else:
        st.success(f"Mukofot: +{info['xp']} XP · +{info['coins']} 🪙" + ("  ·  🏅 Yangi rekord!" if info["new_best"] else ""))
    c1, c2 = st.columns(2)
    c1.button("🔁 Qayta o‘ynash", key="gm_again", on_click=start, args=(key,))
    c2.button("⬅️ O‘yinlar ro‘yxati", key="gm_back2", on_click=leave)


def _norm(s):
    s = str(s).lower()
    for ch in "‘’'`ʻʼ-. ":
        s = s.replace(ch, "")
    return s


def _lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def text_ok(given, answer):
    g, a = _norm(given), _norm(answer)
    return bool(g) and (g == a or (len(a) >= 5 and _lev(g, a) <= 1))


def panel(body, meta=""):
    st.markdown(f'<div class="panel">{f"<div class=qmeta>{meta}</div>" if meta else ""}<div class="qtext">{body}</div></div>',
                unsafe_allow_html=True)


# ============================================================== Ma’lumotlar
CAPITALS = [("O‘zbekiston", "Toshkent"), ("Qozog‘iston", "Astana"), ("Qirg‘iziston", "Bishkek"), ("Tojikiston", "Dushanbe"),
            ("Turkmaniston", "Ashxobod"), ("Rossiya", "Moskva"), ("Xitoy", "Pekin"), ("Yaponiya", "Tokio"),
            ("Janubiy Koreya", "Seul"), ("Turkiya", "Anqara"), ("Germaniya", "Berlin"), ("Fransiya", "Parij"),
            ("Italiya", "Rim"), ("Ispaniya", "Madrid"), ("Buyuk Britaniya", "London"), ("AQSh", "Vashington"),
            ("Kanada", "Ottava"), ("Misr", "Qohira"), ("Avstraliya", "Kanberra"), ("Ozarbayjon", "Boku"),
            ("Ukraina", "Kiyev"), ("Polsha", "Varshava"), ("Norvegiya", "Oslo"), ("Shvetsiya", "Stokgolm"),
            ("Afg‘oniston", "Qobul"), ("Eron", "Tehron"), ("Pokiston", "Islomobod"), ("Hindiston", "Nyu-Dehli")]
CONT_OK = "Avstraliya va Okeaniya"
CONTINENTS = ["Osiyo", "Yevropa", "Afrika", "Shimoliy Amerika", "Janubiy Amerika", CONT_OK]
COUNTRIES = [("O‘zbekiston", "Osiyo"), ("Tojikiston", "Osiyo"), ("Xitoy", "Osiyo"), ("Yaponiya", "Osiyo"), ("Hindiston", "Osiyo"),
             ("Vetnam", "Osiyo"), ("Tailand", "Osiyo"), ("Germaniya", "Yevropa"), ("Fransiya", "Yevropa"), ("Italiya", "Yevropa"),
             ("Ispaniya", "Yevropa"), ("Polsha", "Yevropa"), ("Norvegiya", "Yevropa"), ("Misr", "Afrika"), ("Nigeriya", "Afrika"),
             ("Keniya", "Afrika"), ("Marokash", "Afrika"), ("AQSh", "Shimoliy Amerika"), ("Kanada", "Shimoliy Amerika"),
             ("Meksika", "Shimoliy Amerika"), ("Kuba", "Shimoliy Amerika"), ("Braziliya", "Janubiy Amerika"),
             ("Argentina", "Janubiy Amerika"), ("Peru", "Janubiy Amerika"), ("Chili", "Janubiy Amerika"),
             ("Avstraliya", CONT_OK), ("Yangi Zelandiya", CONT_OK)]
EMOJIS = [("🍎", "Olma"), ("🐱", "Mushuk"), ("🌞", "Quyosh"), ("🚗", "Mashina"), ("📚", "Kitob"), ("✈️", "Samolyot"),
          ("🌳", "Daraxt"), ("🏠", "Uy"), ("🐟", "Baliq"), ("⚽", "Futbol"), ("🌙", "Oy"), ("⭐", "Yulduz"), ("🍞", "Non"),
          ("🐴", "Ot"), ("🎵", "Musiqa"), ("💻", "Kompyuter"), ("🚲", "Velosiped"), ("🔥", "Olov"), ("💧", "Suv"),
          ("🍇", "Uzum"), ("🐄", "Sigir"), ("🕐", "Soat"), ("🔑", "Kalit"), ("☂️", "Soyabon")]
COMPARE = [("Qaysi sayyoraning diametri kattaroq?", "km",
            [("Merkuriy", 4879), ("Venera", 12104), ("Yer", 12742), ("Mars", 6779), ("Yupiter", 139820),
             ("Saturn", 116460), ("Uran", 50724), ("Neptun", 49244)]),
           ("Qaysi cho‘qqi balandroq?", "m",
            [("Everest", 8849), ("K2", 8611), ("Elbrus", 5642), ("Kilimanjaro", 5895), ("Monblan", 4806),
             ("Fudzi", 3776), ("Akonkagua", 6961), ("Denali", 6190)])]
STROOP = [("QIZIL", "#ef4444"), ("KO‘K", "#3b82f6"), ("YASHIL", "#22c55e"), ("SARIQ", "#eab308"),
          ("BINAFSHA", "#a855f7"), ("TO‘Q SARIQ", "#f97316")]
WORDS5 = ["kitob", "qalam", "bahor", "daryo", "osmon", "gilam", "paxta", "sabzi", "piyoz", "olcha", "bozor", "tarix",
          "kimyo", "mashq", "dasht", "shoir", "mouse", "phone", "cloud", "pixel", "logic", "array", "input", "print", "class"]
HANG_WORDS = ["python", "kompyuter", "algoritm", "internet", "dasturchi", "klaviatura", "protsessor", "brauzer",
              "sichqoncha", "monitor", "printer", "matematika", "geografiya", "informatika", "veb"]
ANAGRAMS = ["kitob", "maktab", "daftar", "qalam", "kompyuter", "klaviatura", "internet", "algoritm", "sichqoncha",
            "monitor", "printer", "brauzer", "papka", "dasturlash", "matematika"]
EMO_CARDS = ["🍎", "🚗", "🐱", "⚽", "🌞", "🎵", "🚀", "🍕", "🐶", "🌈"]
LADDER = [100, 200, 300, 500, 1000, 2000, 4000, 8000, 16000, 32000]


# ============================================================== Manbalar (savollar generatorlari)
def mcq(q, options, answer, expl="", html_q=None, qid=None):
    return {"kind": "mcq", "q": q, "html": html_q, "options": options, "answer": answer, "expl": expl, "qid": qid}


def _bank(n, subject=None):
    pool = K.get_questions(subject=subject)
    random.shuffle(pool)
    out = []
    while pool and len(out) < n:
        out.extend(pool[:n - len(out)])
        random.shuffle(pool)
    return out


def _from_bank(q):
    o = list(q["options"])
    random.shuffle(o)
    return mcq(q["question"], o, q["answer"], q.get("explanation", ""), qid=q["id"])


def src_bank(n):
    return [_from_bank(q) for q in _bank(n)], {}


def src_tf(n):
    out = []
    for q in _bank(n):
        truth = random.random() < 0.5
        shown = q["answer"] if truth else random.choice([o for o in q["options"] if o != q["answer"]])
        ans = "✅ To‘g‘ri" if truth else "❌ Noto‘g‘ri"
        out.append(mcq(f"{q['question']}\n\nTaklif: «{shown}»", ["✅ To‘g‘ri", "❌ Noto‘g‘ri"], ans,
                       f"To‘g‘ri javob: {q['answer']}. {q.get('explanation', '')}", qid=q["id"]))
    return out, {}


def src_bank_text(n):
    pool = [q for q in K.get_questions() if 0 < len(q["answer"].strip()) <= 24]
    random.shuffle(pool)
    out = []
    for q in pool[:n]:
        a = q["answer"].strip()
        out.append({"kind": "text", "q": q["question"], "html": None, "options": [], "answer": a,
                    "expl": q.get("explanation", ""), "qid": q["id"],
                    "hint": f"{len(a)} ta belgi, «{a[0]}» harfi bilan boshlanadi"})
    return out, {}


def src_progressive(n):
    pool = K.get_questions()
    by = {d: [q for q in pool if q["difficulty"] == d] for d in K.DIFFS}
    for v in by.values():
        random.shuffle(v)
    chosen, rest = [], []
    for d in K.DIFFS:
        chosen += by[d][:3]
        rest += by[d][3:]
    random.shuffle(rest)
    chosen += rest[:max(0, n - len(chosen))]
    order = {d: i for i, d in enumerate(K.DIFFS)}
    chosen.sort(key=lambda q: order.get(q["difficulty"], 0))
    return [_from_bank(q) for q in chosen[:n]], {}


def src_wheel(n):
    subs = K.subjects()
    subj = random.choice(subs) if subs else None
    mult = random.choice([1, 2, 3])
    items = [_from_bank(q) for q in _bank(n, subj)]
    return items, {"mult": mult, "banner": f"🎰 G‘ildirak aylandi: fan — {subj}, ball ko‘paytirgichi — x{mult}"}


def num_opts(ans, span=None):
    span = span or max(3, abs(ans) // 5 + 3)
    s = {ans}
    while len(s) < 4:
        s.add(ans + random.choice([-1, 1]) * random.randint(1, span))
    o = [str(x) for x in s]
    random.shuffle(o)
    return o


def src_math(n):
    out = []
    for k in range(n):
        lvl = min(k // 8, 4)
        hi = 10 + lvl * 12
        op = random.choice(["+", "-", "×"] + (["÷"] if lvl >= 1 else []))
        if op == "+":
            a, b = random.randint(2, hi), random.randint(2, hi)
            ans = a + b
        elif op == "-":
            a = random.randint(5, hi + 10)
            b = random.randint(1, a)
            ans = a - b
        elif op == "×":
            a, b = random.randint(2, 6 + lvl * 2), random.randint(2, 9 + lvl)
            ans = a * b
        else:
            b, ans = random.randint(2, 9), random.randint(2, 9 + lvl * 3)
            a = b * ans
        out.append(mcq(f"{a} {op} {b} = ?", num_opts(ans), str(ans)))
    return out, {}


def src_seq(n):
    out = []
    for _ in range(n):
        t = random.choice(["ar", "geo", "sq", "fib", "alt"])
        if t == "ar":
            a, d = random.randint(1, 20), random.randint(2, 9)
            seq, rule = [a + d * k for k in range(6)], f"har safar +{d} qo‘shiladi"
        elif t == "geo":
            a, r = random.randint(1, 4), random.randint(2, 3)
            seq, rule = [a * r ** k for k in range(6)], f"har safar ×{r} ga ko‘paytiriladi"
        elif t == "sq":
            s = random.randint(1, 5)
            seq, rule = [(s + k) ** 2 for k in range(6)], "natural sonlarning kvadratlari"
        elif t == "fib":
            a, b = random.randint(1, 5), random.randint(1, 5)
            seq = [a, b]
            while len(seq) < 6:
                seq.append(seq[-1] + seq[-2])
            rule = "har son oldingi ikkitasining yig‘indisi"
        else:
            a, d1, d2 = random.randint(1, 10), random.randint(1, 5), random.randint(6, 9)
            seq = [a]
            for k in range(5):
                seq.append(seq[-1] + (d1 if k % 2 == 0 else d2))
            rule = f"navbat bilan +{d1} va +{d2}"
        out.append(mcq(", ".join(map(str, seq[:5])) + ", ?", num_opts(seq[5]), str(seq[5]), "Qonuniyat: " + rule))
    return out, {}


def src_capitals(n):
    out = []
    for c, cap in random.sample(CAPITALS, min(n, len(CAPITALS))):
        o = [cap] + random.sample([x[1] for x in CAPITALS if x[1] != cap], 3)
        random.shuffle(o)
        out.append(mcq(f"{c} poytaxti qaysi shahar?", o, cap))
    return out, {}


def src_continents(n):
    out = []
    for c, cont in random.sample(COUNTRIES, min(n, len(COUNTRIES))):
        o = [cont] + random.sample([x for x in CONTINENTS if x != cont], 3)
        random.shuffle(o)
        out.append(mcq(f"{c} qaysi qit’ada joylashgan?", o, cont))
    return out, {}


def src_emoji(n):
    out = []
    for em, name in random.sample(EMOJIS, min(n, len(EMOJIS))):
        o = [name] + random.sample([x[1] for x in EMOJIS if x[1] != name], 3)
        random.shuffle(o)
        out.append(mcq("Bu nima?", o, name, html_q=f'<div style="font-size:4rem;text-align:center">{em}</div>'))
    return out, {}


def src_compare(n):
    out = []
    while len(out) < n:
        qtext, unit, data = random.choice(COMPARE)
        a, b = random.sample(data, 2)
        if a[1] == b[1]:
            continue
        win = a if a[1] > b[1] else b
        out.append(mcq(qtext, [a[0], b[0]], win[0], f"{a[0]}: {a[1]:,} {unit} · {b[0]}: {b[1]:,} {unit}".replace(",", " ")))
    return out, {}


def src_stroop(n):
    out = []
    for _ in range(n):
        (word, _c1), (ink_name, ink) = random.choice(STROOP), random.choice(STROOP)
        opts = [ink_name] + random.sample([x[0] for x in STROOP if x[0] != ink_name], 3)
        random.shuffle(opts)
        big = f'<div style="font-size:3.4rem;font-weight:800;text-align:center;color:{ink}">{esc(word)}</div>'
        out.append(mcq("Yozuv RANGINI tanlang (so‘zni emas!)", opts, ink_name, html_q=big))
    return out, {}


def src_anagram(n):
    out = []
    for w in random.sample(ANAGRAMS, min(n, len(ANAGRAMS))):
        letters = list(w)
        for _ in range(10):
            random.shuffle(letters)
            if "".join(letters) != w:
                break
        big = f'<div style="font-size:2.4rem;font-weight:800;letter-spacing:.25em;text-align:center">{esc(" ".join(letters).upper())}</div>'
        out.append({"kind": "text", "q": "Harflardan so‘z tuzing", "html": big, "options": [], "answer": w, "expl": "",
                    "qid": None, "hint": f"{len(w)} harfli, «{w[0]}» bilan boshlanadi"})
    return out, {}


# ============================================================== Umumiy dvigatel (18 ta o‘yin)
def _pts(cfg, i):
    p = cfg.get("pts", 100)
    return p[min(i, len(p) - 1)] if isinstance(p, list) else p


def _advance(cfg, g):
    g["i"] += 1
    if (g["lives"] is not None and g["lives"] <= 0) or g["i"] >= len(g["items"]):
        g["phase"] = "end"
        return
    g["phase"] = "bet" if cfg.get("mode") == "wager" else "ask"
    if cfg.get("per_q"):
        g["deadline"] = time.time() + cfg["per_q"]


def _answer(cfg, g, given):
    it = g["items"][g["i"]]
    ok = given is not None and (text_ok(given, it["answer"]) if it["kind"] == "text" else given == it["answer"])
    mode, base, gained = cfg.get("mode"), _pts(cfg, g["i"]), 0
    if ok:
        g["correct"] += 1
        g["streak"] += 1
        if mode == "wager":
            gained = g["bet"]
        elif mode != "ladder":
            gained = int(base * g["mult"]) + (min(g["streak"] - 1, 4) * 10 if cfg.get("streak_bonus") else 0)
    else:
        g["wrong"] += 1
        g["streak"] = 0
        if mode == "wager":
            gained = -g["bet"]
        else:
            gained = cfg.get("wrong", 0)
        if g["lives"] is not None:
            g["lives"] -= 1
    g["score"] += gained
    if mode == "ladder":
        if ok:
            g["score"] = LADDER[g["i"]]
        else:
            safe = 2000 if g["i"] > 5 else 300 if g["i"] > 2 else 0
            g["score"], g["lives"] = safe, 0
    if cfg.get("bot") and random.random() < cfg["bot"]:
        g["bot"] += base
    g["last"] = {"ok": ok, "given": given, "answer": it["answer"], "expl": it.get("expl", ""), "gained": gained,
                 "timeout": given is None}
    if it.get("qid"):
        with K.conn() as c:
            K.record_stat(c, it["qid"], ok)
    if cfg.get("fb"):
        g["phase"] = "fb"
    else:
        _advance(cfg, g)


def engine(key, cfg):
    g = G()
    if "items" not in g:
        items, extra = cfg["src"](cfg["n"])
        if not items:
            st.warning("Bu o‘yin uchun savollar yetarli emas. Savollar bankiga savol qo‘shing.")
            return
        now = time.time()
        g.update(items=items, i=0, score=cfg.get("start", 0), correct=0, wrong=0, lives=cfg.get("lives"), streak=0,
                 phase="bet" if cfg.get("mode") == "wager" else "ask", started=now,
                 deadline=(now + cfg["per_q"]) if cfg.get("per_q") else None, bet=0, last=None, bot=0,
                 mult=extra.get("mult", 1), banner=extra.get("banner"))
    n, now = len(g["items"]), time.time()
    if g["phase"] != "end" and cfg.get("total_time") and now >= g["started"] + cfg["total_time"]:
        g["phase"] = "end"
    if g["phase"] in ("ask", "bet") and (cfg.get("total_time") or cfg.get("per_q")):
        st_autorefresh(interval=1000, key="gm_tick")
    if g["phase"] == "ask" and cfg.get("per_q") and now >= g["deadline"]:
        _answer(cfg, g, None)
        st.rerun()
    if g["phase"] == "end":
        return engine_end(key, cfg, g)

    c = st.columns(4)
    c[0].metric("⭐ Ball", g["score"])
    if g["lives"] is not None:
        c[1].metric("Jon", "❤️" * max(g["lives"], 0) or "💀")
    else:
        c[1].metric("🔥 Seriya", g["streak"])
    if cfg.get("total_time"):
        c[2].metric("⏱️ Vaqt", f"{max(0, math.ceil(g['started'] + cfg['total_time'] - now))} s")
    elif cfg.get("per_q") and g["phase"] == "ask":
        c[2].metric("⏱️ Vaqt", f"{max(0, math.ceil(g['deadline'] - now))} s")
    else:
        c[2].metric("⏱️ Vaqt", "—")
    c[3].metric("📋 Savol", f"{min(g['i'] + 1, n)}/{n}")
    if g.get("banner"):
        st.info(g["banner"])
    if cfg.get("bot"):
        st.caption(f"🤖 Bot balli: {g['bot']}")
    if cfg.get("mode") == "ladder":
        nxt = LADDER[min(g["i"], n - 1)]
        st.caption(f"💰 Hozirgi sovrin: {g['score']} · Keyingi savol uchun: {nxt} · Xavfsiz nuqtalar: 300 va 2000")

    it = g["items"][g["i"]]
    if it["html"]:
        body = it["html"] + (f'<div class="qmeta" style="text-align:center">{esc(it["q"])}</div>' if it["q"] else "")
    else:
        body = esc(it["q"]).replace("\n", "<br>")

    if g["phase"] == "bet":
        panel("Tikish vaqti! Bu savolga qancha ball tikasiz? To‘g‘ri javobda yutasiz, xatoda yo‘qotasiz.")
        cols = st.columns(len(cfg["bets"]))
        for col, b in zip(cols, cfg["bets"]):
            with col:
                if H["btn"](f"🎲 {b} ball", key=f"gmbet{b}_{g['i']}"):
                    g["bet"], g["phase"] = b, "ask"
                    st.rerun()
        return

    if g["phase"] == "ask":
        if g.get("last") and not cfg.get("fb"):
            l = g["last"]
            st.caption(("✅ To‘g‘ri" if l["ok"] else f"❌ Noto‘g‘ri · javob: {l['answer']}") + (f" · {l['gained']:+d}" if l["gained"] else ""))
        panel(body)
        if cfg.get("mode") == "wager":
            st.caption(f"🎲 Tikilgan: {g['bet']} ball")
        if it["kind"] == "mcq":
            two = len(it["options"]) == 2
            cols = st.columns(2) if two else [st.container()] * 1
            for j, opt in enumerate(it["options"]):
                with (cols[j] if two else cols[0]):
                    if H["btn"](f"{chr(65 + j)} · {opt}" if not two else opt, key=f"qoptg{j}_{g['i']}"):
                        _answer(cfg, g, opt)
                        st.rerun()
        else:
            if it.get("hint"):
                st.caption("💡 " + it["hint"])
            with st.form(f"gmt_{g['i']}", clear_on_submit=True):
                txt = st.text_input("Javobingiz", key=f"gmtx_{g['i']}")
                sub = st.form_submit_button("Yuborish")
            if sub:
                _answer(cfg, g, txt)
                st.rerun()
        return

    # fb — javobdan keyingi izoh
    l = g["last"]
    panel(body)
    if l["ok"]:
        st.success(f"✅ To‘g‘ri! {l['gained']:+d} ball" if l["gained"] else "✅ To‘g‘ri!")
    elif l["timeout"]:
        st.warning(f"⏰ Vaqt tugadi. To‘g‘ri javob: {l['answer']}" + (f" ({l['gained']:+d})" if l["gained"] else ""))
    else:
        st.error(f"❌ Noto‘g‘ri. To‘g‘ri javob: {l['answer']}" + (f" ({l['gained']:+d})" if l["gained"] else ""))
    if l["expl"]:
        st.info("💡 " + l["expl"])
    if cfg.get("mode") == "ladder" and l["ok"] and g["i"] < n - 1:
        a, b = st.columns(2)
        if a.button(f"💰 Pulni olish ({g['score']})", key="gm_cash"):
            g["phase"] = "end"
            st.rerun()
        if b.button("➡️ Davom etish", key="gm_cont"):
            _advance(cfg, g)
            st.rerun()
    else:
        last = g["i"] + 1 >= n or (g["lives"] is not None and g["lives"] <= 0)
        if st.button("🏁 Natijani ko‘rish" if last else "➡️ Keyingi", key=f"gm_next{g['i']}"):
            _advance(cfg, g)
            st.rerun()


def engine_end(key, cfg, g):
    n = len(g["items"])
    goal = cfg.get("goal", n)
    perf = min(1.0, g["correct"] / max(goal, 1))
    stats = [("🎯 To‘g‘ri", f"{g['correct']}/{g['correct'] + g['wrong']}"), ("❌ Xato", g["wrong"])]
    note = ""
    if cfg.get("bot"):
        win = g["score"] > g["bot"]
        perf = min(1.0, 0.8 * g["correct"] / n + (0.2 if win else 0))
        stats.append(("🤖 Bot", g["bot"]))
        note = "🏆 Siz botni yengdingiz!" if win else ("🤝 Durang!" if g["score"] == g["bot"] else "🤖 Bot g‘olib bo‘ldi — qayta urinib ko‘ring!")
    end_screen(key, max(g["score"], 0) if cfg.get("mode") != "wager" else g["score"], perf, stats, note)


# ============================================================== Maxsus o‘yinlar (12 ta)
def game_flash():
    g = G()
    if "cards" not in g:
        pool = K.get_questions()
        if not pool:
            st.warning("Savollar bankida savol yo‘q.")
            return
        g.update(cards=random.sample(pool, min(10, len(pool))), i=0, show=False, known=0)
    cards = g["cards"]
    if g["i"] >= len(cards):
        return end_screen("flash", g["known"] * 10, g["known"] / len(cards), [("✅ Bildim", f"{g['known']}/{len(cards)}")],
                          "Bilmagan savollaringizni «Savollar bilan o‘ynash» o‘yinlarida takrorlang.")
    c = cards[g["i"]]
    st.progress(g["i"] / len(cards), text=f"Karta {g['i'] + 1}/{len(cards)}")
    panel(esc(c["question"]), esc(c["subject"]))
    if not g["show"]:
        if H["btn"]("👁 Javobni ko‘rsat", key=f"gmf_show{g['i']}"):
            g["show"] = True
            st.rerun()
    else:
        st.success(f"Javob: {c['answer']}")
        if c.get("explanation"):
            st.info("💡 " + c["explanation"])
        a, b = st.columns(2)
        if a.button("✅ Bildim", key=f"gmf_ok{g['i']}"):
            g["known"] += 1
            g["i"] += 1
            g["show"] = False
            st.rerun()
        if b.button("🔁 Yana takrorlayman", key=f"gmf_no{g['i']}"):
            g["i"] += 1
            g["show"] = False
            st.rerun()


def game_match():
    g = G()
    if "pairs" not in g:
        pool = K.get_questions()
        random.shuffle(pool)
        uniq = {}
        for q in pool:
            if q["answer"] not in uniq and len(uniq) < 5:
                uniq[q["answer"]] = q
        if len(uniq) < 3:
            st.warning("Moslashtirish uchun kamida 3 ta har xil javobli savol kerak.")
            return
        pairs = list(uniq.values())
        opts = [q["answer"] for q in pairs]
        random.shuffle(opts)
        g.update(pairs=pairs, opts=opts, done=False)
    if not g["done"]:
        st.caption("Har bir savolga to‘g‘ri javobni moslang.")
        with st.form("gm_match"):
            picks = [st.selectbox(f"{i + 1}. {q['question']}", ["— tanlang —"] + g["opts"], key=f"gmm{i}") for i, q in enumerate(g["pairs"])]
            sub = st.form_submit_button("Tekshirish")
        if sub:
            if any(p.startswith("—") for p in picks):
                st.error("Hamma savolga javob tanlang.")
            else:
                g["picks"] = picks
                g["correct"] = sum(p == q["answer"] for p, q in zip(picks, g["pairs"]))
                g["done"] = True
                st.rerun()
    else:
        n = len(g["pairs"])
        for p, q in zip(g["picks"], g["pairs"]):
            st.write(("✅ " if p == q["answer"] else "❌ ") + f"{q['question']} → **{q['answer']}**" + ("" if p == q["answer"] else f" (siz: {p})"))
        end_screen("match", g["correct"] * 100, g["correct"] / n, [("🎯 To‘g‘ri", f"{g['correct']}/{n}")])


def game_guess():
    g = G()
    if "secret" not in g:
        g.update(secret=random.randint(1, 100), tries=0, hist=[], won=False)
    mx = 7
    if g["won"] or g["tries"] >= mx:
        score = (mx - g["tries"] + 1) * 100 if g["won"] else 0
        return end_screen("guess", score, (mx - g["tries"] + 1) / mx if g["won"] else 0.1,
                          [("🔢 Urinish", g["tries"])], "Son: " + str(g["secret"]))
    st.markdown('<div class="panel"><div class="qtext">1 dan 100 gacha sonni toping</div></div>', unsafe_allow_html=True)
    st.progress(g["tries"] / mx, text=f"Urinishlar: {g['tries']}/{mx}")
    with st.form("gm_guess", clear_on_submit=True):
        v = st.number_input("Taxmin", 1, 100, 50, step=1)
        sub = st.form_submit_button("Taxmin qilish")
    if sub:
        v = int(v)
        g["tries"] += 1
        if v == g["secret"]:
            g["won"] = True
        else:
            g["hist"].append(f"{v} → {'⬇️ kichikroq' if v > g['secret'] else '⬆️ kattaroq'}")
        st.rerun()
    for h in g["hist"]:
        st.markdown(f'<span class="chip">{esc(h)}</span>', unsafe_allow_html=True)


def eval_guess(guess, target):
    res = ["gray"] * 5
    left = list(target)
    for i in range(5):
        if guess[i] == target[i]:
            res[i] = "green"
            left.remove(guess[i])
    for i in range(5):
        if res[i] == "gray" and guess[i] in left:
            res[i] = "yellow"
            left.remove(guess[i])
    return res


def game_wordle():
    g = G()
    if "target" not in g:
        g.update(target=random.choice(WORDS5), guesses=[])
    col = {"green": "#22c55e", "yellow": "#d89e00", "gray": "#475569"}
    rows = ""
    for gu in g["guesses"]:
        r = eval_guess(gu, g["target"])
        rows += '<div class="wrow">' + "".join(f'<div class="wt" style="background:{col[c]}">{esc(ch.upper())}</div>' for ch, c in zip(gu, r)) + "</div>"
    for _ in range(6 - len(g["guesses"])):
        rows += '<div class="wrow">' + '<div class="wt"></div>' * 5 + "</div>"
    st.markdown(rows, unsafe_allow_html=True)
    solved = bool(g["guesses"]) and g["guesses"][-1] == g["target"]
    if solved or len(g["guesses"]) >= 6:
        return end_screen("wordle", (7 - len(g["guesses"])) * 100 if solved else 0, (7 - len(g["guesses"])) / 6 if solved else 0.1,
                          [("🔤 Urinish", len(g["guesses"]))], "So‘z: " + g["target"].upper())
    st.caption("5 harfli so‘z kiriting (o‘zbek yoki ingliz, lotin harflarida). 🟩 — o‘z joyida, 🟨 — so‘zda bor, lekin boshqa joyda.")
    with st.form("gm_wordle", clear_on_submit=True):
        w = st.text_input("So‘z", max_chars=5)
        sub = st.form_submit_button("Tekshirish")
    if sub:
        w = w.strip().lower()
        if len(w) == 5 and w.isascii() and w.isalpha():
            g["guesses"].append(w)
            st.rerun()
        else:
            st.error("Aynan 5 ta lotin harfi kiriting.")


def game_hang():
    g = G()
    if "word" not in g:
        g.update(word=random.choice(HANG_WORDS), guessed=[], wrong=0)
    faces = ["😀", "🙂", "😐", "😟", "😨", "😱", "💀"]
    won = all(ch in g["guessed"] for ch in g["word"])
    if won or g["wrong"] >= 6:
        return end_screen("hang", (7 - g["wrong"]) * 100 if won else 0, 0.6 + 0.4 * (6 - g["wrong"]) / 6 if won else 0.1,
                          [("❌ Xato", g["wrong"])], "So‘z: " + g["word"].upper())
    shown = " ".join(ch.upper() if ch in g["guessed"] else "_" for ch in g["word"])
    st.markdown(f'<div class="panel"><div class="bigw">{shown}</div><div style="text-align:center;font-size:2rem">{faces[g["wrong"]]} '
                f'{"❤️" * (6 - g["wrong"])}</div></div>', unsafe_allow_html=True)

    def pick(ch):
        g["guessed"].append(ch)
        if ch not in g["word"]:
            g["wrong"] += 1
    letters = "abcdefghijklmnopqrstuvwxyz"
    cols = st.columns(9)
    for idx, ch in enumerate(letters):
        with cols[idx % 9]:
            st.button(ch.upper(), key=f"gmh_{ch}", disabled=ch in g["guessed"], on_click=pick, args=(ch,))


def game_digits():
    g = G()
    if "level" not in g:
        g.update(level=3, phase="new", passed=0)
    if g["phase"] == "new":
        g.update(seq="".join(random.choice("0123456789") for _ in range(g["level"])), shown=time.time(), phase="show")
    if g["phase"] == "end":
        return end_screen("digits", g["passed"] * 100, min(1.0, g["passed"] / 8), [("🧠 Darajalar", g["passed"])],
                          f"Oxirgi raqamlar: {g['seq']}")
    if g["phase"] == "show":
        dur = 1.0 + 0.7 * g["level"]
        if time.time() >= g["shown"] + dur:
            g["phase"] = "type"
            st.rerun()
        st_autorefresh(interval=500, key="gm_digit_tick")
        st.markdown(f'<div class="panel"><div class="qmeta">Eslab qoling! Daraja {g["level"] - 2}</div>'
                    f'<div class="bigw">{esc(" ".join(g["seq"]))}</div></div>', unsafe_allow_html=True)
        return
    st.markdown(f'<div class="panel"><div class="qtext">Qanday raqamlarni ko‘rdingiz? ({g["level"]} ta)</div></div>', unsafe_allow_html=True)
    with st.form("gm_digits", clear_on_submit=True):
        v = st.text_input("Raqamlar", max_chars=12)
        sub = st.form_submit_button("Tekshirish")
    if sub:
        if v.replace(" ", "") == g["seq"]:
            g["passed"] += 1
            g["level"] += 1
            g["phase"] = "new"
        else:
            g["phase"] = "end"
        st.rerun()


def game_memory():
    g = G()
    if "cards" not in g:
        cards = random.sample(EMO_CARDS, 6) * 2
        random.shuffle(cards)
        g.update(cards=cards, matched=[], flipped=[], moves=0)

    def flip(i):
        if len(g["flipped"]) == 2:
            g["flipped"] = []
        if i in g["flipped"] or i in g["matched"]:
            return
        g["flipped"].append(i)
        if len(g["flipped"]) == 2:
            g["moves"] += 1
            a, b = g["flipped"]
            if g["cards"][a] == g["cards"][b]:
                g["matched"] += [a, b]
                g["flipped"] = []
    if len(g["matched"]) == 12:
        return end_screen("memory", max(100, 1000 - (g["moves"] - 6) * 60), max(0.3, 1 - (g["moves"] - 6) / 12),
                          [("🔁 Yurishlar", g["moves"])])
    st.caption(f"Yurishlar: {g['moves']} · Topilgan juftliklar: {len(g['matched']) // 2}/6")
    for r in range(3):
        cols = st.columns(4)
        for cc in range(4):
            i = r * 4 + cc
            show = i in g["matched"] or i in g["flipped"]
            with cols[cc]:
                st.button(g["cards"][i] if show else "❓", key=f"gmc{i}", disabled=i in g["matched"], on_click=flip, args=(i,))


TTT_WINS = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def ttt_winner(b):
    for x, y, z in TTT_WINS:
        if b[x] and b[x] == b[y] == b[z]:
            return b[x]
    return None


def ttt_bot(b):
    free = [i for i, v in enumerate(b) if not v]
    if random.random() < 0.15:
        return random.choice(free)
    for me_, op in (("O", "O"), ("O", "X")):  # avval yutish, keyin to‘sish
        for x, y, z in TTT_WINS:
            line = [b[x], b[y], b[z]]
            if line.count(op) == 2 and line.count("") == 1:
                return (x, y, z)[line.index("")]
    for pref in ([4], [0, 2, 6, 8], [1, 3, 5, 7]):
        opts = [i for i in pref if not b[i]]
        if opts:
            return random.choice(opts)
    return random.choice(free)


def game_ttt():
    g = G()
    if "b" not in g:
        g["b"] = [""] * 9

    def move(i):
        b = g["b"]
        if b[i] or ttt_winner(b):
            return
        b[i] = "X"
        if not ttt_winner(b) and "" in b:
            b[ttt_bot(b)] = "O"
    w = ttt_winner(g["b"])
    if w or "" not in g["b"]:
        res = {"X": ("Siz yutdingiz! 🎉", 300, 1.0), "O": ("Bot yutdi 🤖", 0, 0.1), None: ("Durang 🤝", 150, 0.5)}[w]
        return end_screen("ttt", res[1], res[2], [("Natija", "G‘alaba" if w == "X" else "Mag‘lubiyat" if w else "Durang")], res[0])
    st.caption("Siz — ❌, bot — ⭕. Uch xonani bir qatorga joylashtiring.")
    for r in range(3):
        cols = st.columns(3)
        for cc in range(3):
            i = r * 3 + cc
            v = g["b"][i]
            with cols[cc]:
                st.button({"X": "❌", "O": "⭕", "": "·"}[v], key=f"gmt{i}", disabled=bool(v), on_click=move, args=(i,))


def game_sort():
    g = G()
    if "nums" not in g:
        g.update(nums=random.sample(range(1, 100), 8), picked=[], mistakes=0, started=time.time(), t=None)

    def pick(n):
        rem = [x for x in g["nums"] if x not in g["picked"]]
        if n == min(rem):
            g["picked"].append(n)
            if len(g["picked"]) == len(g["nums"]):
                g["t"] = time.time() - g["started"]
        else:
            g["mistakes"] += 1
    if g["t"] is not None:
        score = max(100, 1000 - g["mistakes"] * 100 - int(g["t"]) * 10)
        return end_screen("sort", score, max(0.1, 1 - g["mistakes"] * 0.15 - max(0, g["t"] - 20) / 60),
                          [("❌ Xato", g["mistakes"]), ("⏱️ Vaqt", f"{g['t']:.0f} s")])
    st.markdown('<div class="panel"><div class="qtext">Sonlarni KICHIKDAN KATTAGA qarab bosing</div></div>', unsafe_allow_html=True)
    st.caption(f"Tanlandi: {' → '.join(map(str, g['picked'])) or '—'} · Xatolar: {g['mistakes']}")
    rem = [x for x in g["nums"] if x not in g["picked"]]
    cols = st.columns(4)
    for idx, n in enumerate(rem):
        with cols[idx % 4]:
            st.button(str(n), key=f"gms{n}", on_click=pick, args=(n,))


def game_code():
    g = G()
    if "secret" not in g:
        g.update(secret="".join(random.sample("0123456789", 4)), hist=[], won=False)
    mx = 8
    if g["won"] or len(g["hist"]) >= mx:
        n = len(g["hist"])
        return end_screen("code", (mx + 1 - n) * 100 if g["won"] else 0, (mx + 1 - n) / mx if g["won"] else 0.1,
                          [("🔢 Urinish", n)], "Kod: " + g["secret"])
    st.markdown('<div class="panel"><div class="qtext">4 xonali maxfiy kodni toping</div>'
                '<div class="qmeta">Raqamlar takrorlanmaydi. 🎯 — o‘z joyida, 🔁 — kodda bor, lekin boshqa joyda.</div></div>', unsafe_allow_html=True)
    st.progress(len(g["hist"]) / mx, text=f"Urinishlar: {len(g['hist'])}/{mx}")
    with st.form("gm_code", clear_on_submit=True):
        v = st.text_input("Kod", max_chars=4)
        sub = st.form_submit_button("Tekshirish")
    if sub:
        if len(v) == 4 and v.isdigit() and len(set(v)) == 4:
            bulls = sum(a == b for a, b in zip(v, g["secret"]))
            cows = len(set(v) & set(g["secret"])) - bulls
            g["hist"].append((v, bulls, cows))
            g["won"] = bulls == 4
            st.rerun()
        else:
            st.error("4 ta turli raqam kiriting.")
    for v, b, c in g["hist"]:
        st.markdown(f'<span class="chip">{v} → 🎯{b} · 🔁{c}</span>', unsafe_allow_html=True)


MS_SIZE, MS_MINES = 5, 4


def _nbrs(r, c):
    return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
            if (dr or dc) and 0 <= r + dr < MS_SIZE and 0 <= c + dc < MS_SIZE]


def game_mines():
    g = G()
    if "mines" not in g:
        g.update(mines=None, revealed=[], over=False)

    def click(r, c):
        if g["over"]:
            return
        if g["mines"] is None:
            cells = [(a, b) for a in range(MS_SIZE) for b in range(MS_SIZE) if (a, b) != (r, c)]
            g["mines"] = random.sample(cells, MS_MINES)
        if (r, c) in [tuple(m) for m in g["mines"]]:
            g["over"] = True
            return
        stack = [(r, c)]
        mset = {tuple(m) for m in g["mines"]}
        while stack:
            cur = stack.pop()
            if cur in g["revealed"] or cur in mset:
                continue
            g["revealed"].append(cur)
            if not any(nb in mset for nb in _nbrs(*cur)):
                stack.extend(_nbrs(*cur))
    safe = MS_SIZE * MS_SIZE - MS_MINES
    won = len(g["revealed"]) == safe
    if g["over"] or won:
        return end_screen("mines", 500 if won else len(g["revealed"]) * 20, 1.0 if won else 0.6 * len(g["revealed"]) / safe,
                          [("🟩 Ochildi", f"{len(g['revealed'])}/{safe}")], "Barcha minalardan qochdingiz! 🎉" if won else "💥 Minaga bosdingiz!")
    st.caption(f"{MS_SIZE}×{MS_SIZE} maydonda {MS_MINES} ta mina bor. Raqam — atrofdagi minalar soni.")
    mset = {tuple(m) for m in (g["mines"] or [])}
    for r in range(MS_SIZE):
        cols = st.columns(MS_SIZE)
        for c in range(MS_SIZE):
            with cols[c]:
                if (r, c) in g["revealed"]:
                    n = sum(nb in mset for nb in _nbrs(r, c))
                    st.button(str(n) if n else "▫️", key=f"gmn{r}{c}", disabled=True)
                else:
                    st.button("⬜", key=f"gmn{r}{c}", on_click=click, args=(r, c))


SNAKE = """
<div style="text-align:center;color:#fff;font-family:Inter,system-ui,sans-serif">
<div>🍎 Ball: <b id="sc">0</b> · Rekord: <b id="hi">0</b></div>
<canvas id="c" width="300" height="300" style="background:#0b1020;border:2px solid #6847ff;border-radius:10px;margin:8px 0"></canvas><br>
<button onclick="dir(0,-1)">⬆️</button><br>
<button onclick="dir(-1,0)">⬅️</button> <button onclick="dir(0,1)">⬇️</button> <button onclick="dir(1,0)">➡️</button><br><br>
<button onclick="reset()">🔄 Boshidan</button>
<div style="opacity:.7;margin-top:6px;font-size:13px">Klaviatura: strelkalar yoki WASD</div></div>
<script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),N=15,S=20;let sn,d,f,sc,hi=0,t,alive;
function reset(){sn=[{x:7,y:7}];d={x:1,y:0};sc=0;alive=true;place();document.getElementById('sc').textContent=0;clearInterval(t);t=setInterval(step,130);}
function place(){do{f={x:Math.floor(Math.random()*N),y:Math.floor(Math.random()*N)}}while(sn.some(s=>s.x==f.x&&s.y==f.y));}
function dir(a,b){if(a==-d.x&&b==-d.y&&sn.length>1)return;d={x:a,y:b};}
function step(){if(!alive)return;const h={x:sn[0].x+d.x,y:sn[0].y+d.y};
 if(h.x<0||h.y<0||h.x>=N||h.y>=N||sn.some(s=>s.x==h.x&&s.y==h.y)){alive=false;hi=Math.max(hi,sc);document.getElementById('hi').textContent=hi;draw();return;}
 sn.unshift(h);if(h.x==f.x&&h.y==f.y){sc++;document.getElementById('sc').textContent=sc;place();}else sn.pop();draw();}
function draw(){x.fillStyle='#0b1020';x.fillRect(0,0,300,300);x.fillStyle='#ef4444';x.fillRect(f.x*S+2,f.y*S+2,S-4,S-4);
 sn.forEach((s,i)=>{x.fillStyle=i?'#22c55e':'#86efac';x.fillRect(s.x*S+1,s.y*S+1,S-2,S-2);});
 if(!alive){x.fillStyle='rgba(0,0,0,.6)';x.fillRect(0,0,300,300);x.fillStyle='#fff';x.font='20px sans-serif';x.textAlign='center';x.fillText('O‘yin tugadi',150,150);}}
document.addEventListener('keydown',e=>{const m={ArrowUp:[0,-1],ArrowDown:[0,1],ArrowLeft:[-1,0],ArrowRight:[1,0],w:[0,-1],s:[0,1],a:[-1,0],d:[1,0]}[e.key];if(m){dir(m[0],m[1]);e.preventDefault();}});
reset();
</script>
"""


def game_snake():
    st.caption("😎 Dam olish o‘yini — XP berilmaydi, faqat zavq uchun!")
    try:
        import streamlit.components.v1 as components
        components.html(SNAKE, height=470)
    except Exception:
        st.warning("O‘yinni ko‘rsatib bo‘lmadi.")


# ============================================================== Ro‘yxatga olish (30 ta)
GAMES, REG = [], {}
CATS = [("bilim", "🧠 Bilim"), ("dunyo", "🌍 Dunyo"), ("raqam", "🔢 Raqamlar"), ("soz", "🔤 So‘zlar"),
        ("mantiq", "🧩 Mantiq"), ("dam", "😎 Dam olish")]


def reg(key, icon, name, cat, desc, fn, reward=True):
    g = {"key": key, "icon": icon, "name": name, "cat": cat, "desc": desc, "fn": fn, "reward": reward}
    GAMES.append(g)
    REG[key] = g


def ereg(key, icon, name, cat, desc, cfg):
    reg(key, icon, name, cat, desc, lambda k=key, c=cfg: engine(k, c))


ereg("blitz", "⚡", "Blitz 60", "bilim", "60 soniyada imkon qadar ko‘p savolga javob bering. Xato −5 ball.",
     dict(src=src_bank, n=60, total_time=60, pts=10, wrong=-5, goal=12))
ereg("survival", "❤️", "Omon qolish", "bilim", "3 ta jon. Har xato — bitta jon yo‘qotish. Qancha davom eta olasiz?",
     dict(src=src_bank, n=40, lives=3, fb=True, pts=100, streak_bonus=True, goal=10))
ereg("tf", "✅", "To‘g‘ri yoki Noto‘g‘ri", "bilim", "Savol va taklif qilingan javob: u to‘g‘rimi? 3 ta jon.",
     dict(src=src_tf, n=15, lives=3, pts=50, goal=12))
ereg("duel", "🤖", "Bot bilan duel", "bilim", "7 ta savol. Botdan ko‘proq ball to‘plang!",
     dict(src=src_bank, n=7, fb=True, pts=100, bot=0.6))
ereg("wager", "🎲", "Xavf-xatar", "bilim", "Har savolga ball tikasiz: to‘g‘ri — yutasiz, xato — yo‘qotasiz.",
     dict(src=src_bank, n=8, mode="wager", bets=[100, 200, 300], fb=True, start=500))
ereg("ladder", "🪜", "Million zinapoyasi", "bilim", "10 pog‘ona. Pulni oling yoki xavf qiling. Xavfsiz nuqtalar bor.",
     dict(src=src_bank, n=10, mode="ladder", fb=True))
ereg("text", "⌨️", "Yozib javob ber", "bilim", "Variantlarsiz! Javobni o‘zingiz yozasiz (kichik xatolar kechiriladi).",
     dict(src=src_bank_text, n=8, lives=4, fb=True, pts=100))
ereg("level", "📈", "Qiyinlashib boradi", "bilim", "Oson → O‘rta → Qiyin. 3 ta jon, har bosqichda ball oshadi.",
     dict(src=src_progressive, n=9, lives=3, fb=True, pts=[100, 100, 100, 200, 200, 200, 300, 300, 300]))
ereg("lightning", "⏱️", "Chaqmoq raundi", "bilim", "Har savolga atigi 5 soniya!",
     dict(src=src_bank, n=15, per_q=5, pts=20, goal=10))
ereg("wheel", "🎰", "Omad g‘ildiragi", "bilim", "G‘ildirak fan va ball ko‘paytirgichini (x1–x3) tanlaydi.",
     dict(src=src_wheel, n=5, fb=True, pts=100))
reg("match", "🔗", "Moslashtirish", "bilim", "5 ta savolga to‘g‘ri javoblarni moslang.", game_match)
reg("flash", "🧠", "Takrorlash kartalari", "bilim", "Kartani oching, javobni eslang va o‘zingizni baholang.", game_flash)

ereg("capitals", "🏛️", "Poytaxtni top", "dunyo", "Davlat poytaxtini toping. Har savolga 12 soniya.",
     dict(src=src_capitals, n=10, per_q=12, fb=True, pts=100))
ereg("continents", "🌐", "Qit’ani top", "dunyo", "Davlat qaysi qit’ada joylashgan?",
     dict(src=src_continents, n=10, per_q=10, pts=60))
ereg("emoji", "😀", "Emoji topishmoq", "dunyo", "Rasm (emoji) nimani anglatadi?", dict(src=src_emoji, n=10, pts=50))
ereg("compare", "📏", "Qaysi kattaroq?", "dunyo", "Sayyoralar va cho‘qqilarni solishtiring. 2 ta jon.",
     dict(src=src_compare, n=25, lives=2, pts=50, goal=12))

ereg("math", "➕", "Matematika blitz", "raqam", "60 soniyada misollar yeching. Misollar murakkablashib boradi.",
     dict(src=src_math, n=80, total_time=60, pts=10, wrong=-5, goal=15))
ereg("seq", "🔁", "Sonlar ketma-ketligi", "raqam", "Keyingi sonni toping: qonuniyatni aniqlang.",
     dict(src=src_seq, n=8, fb=True, pts=100))
reg("guess", "🔢", "Sonni top", "raqam", "1–100 oralig‘ida son o‘ylandi. 7 urinishda toping.", game_guess)
reg("digits", "🧠", "Raqamlar xotirasi", "raqam", "Raqamlarni ko‘ring, eslab qoling va yozing. Har bosqichda uzayadi.", game_digits)
reg("sort", "📶", "Sonlarni tartiblash", "raqam", "8 ta sonni kichikdan kattaga bosing. Tezlik muhim!", game_sort)
reg("code", "🔐", "Kod buzar", "raqam", "4 xonali maxfiy kodni 8 urinishda toping (Mastermind).", game_code)

reg("wordle", "🔤", "So‘z topish", "soz", "5 harfli so‘zni 6 urinishda toping (Wordle).", game_wordle)
reg("hang", "😱", "Osilgan odam", "soz", "Harflarni tanlab, yashirin so‘zni toping. 6 ta xato mumkin.", game_hang)
ereg("anagram", "🔀", "So‘z aralashmasi", "soz", "Aralashib ketgan harflardan so‘z tuzing.",
     dict(src=src_anagram, n=6, fb=True, pts=100))

reg("memory", "🃏", "Xotira kartalari", "mantiq", "12 ta kartadan bir xil juftliklarni toping.", game_memory)
reg("ttt", "❌", "Krestik-nolik", "mantiq", "Bot bilan 3×3 maydonda o‘ynang.", game_ttt)
ereg("stroop", "🎨", "Ranglar tuzog‘i", "mantiq", "So‘z emas, yozuv RANGINI tanlang! 40 soniya.",
     dict(src=src_stroop, n=60, total_time=40, pts=15, wrong=-10, goal=15))
reg("mines", "💣", "Mina qidiruvchi", "mantiq", "5×5 maydonda minalarga tegmasdan barcha xavfsiz katakni oching.", game_mines)

reg("snake", "🐍", "Ilon", "dam", "Klassik Snake. XP berilmaydi — dam olish uchun.", game_snake, reward=False)

GAME_CSS = """<style>
.wrow{display:flex;gap:6px;justify-content:center;margin:5px 0}
.wt{width:52px;height:52px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:800;
 border-radius:8px;color:#fff;border:2px solid rgba(255,255,255,.2);background:rgba(255,255,255,.05)}
.bigw{font-size:2.4rem;font-weight:800;letter-spacing:.25em;text-align:center;padding:6px}
.gcard{min-height:128px}
</style>"""


# ============================================================== O‘yinlar markazi sahifasi
def page_games():
    u = me()
    st.markdown(GAME_CSS, unsafe_allow_html=True)
    key = st.session_state.get("gm_active")
    if key in REG:
        g = REG[key]
        a, b = st.columns([1, 4])
        a.button("⬅️ Ro‘yxat", key="gm_back", on_click=leave)
        b.markdown(f"### {g['icon']} {g['name']}")
        st.caption(g["desc"])
        return g["fn"]()
    st.title("🕹️ O‘yinlar markazi")
    used = K.game_xp_today(u["id"])
    st.progress(min(1.0, used / K.GAME_XP_CAP), text=f"Bugungi mini-o‘yin XP: {used}/{K.GAME_XP_CAP} (limit har kuni yangilanadi)")
    best = K.game_best(u["id"])
    played = len(best)
    st.caption(f"🎯 Siz sinab ko‘rgan o‘yinlar: {played}/{len(GAMES) - 1} · 5, 15 va 30 ta o‘yin uchun maxsus yutuqlar bor!")
    tabs = st.tabs([lab for _, lab in CATS] + ["🏆 Rekordlar"])
    for tab, (cat, _) in zip(tabs, CATS):
        with tab:
            items = [g for g in GAMES if g["cat"] == cat]
            for row in range(0, len(items), 3):
                cols = st.columns(3)
                for col, g in zip(cols, items[row:row + 3]):
                    with col:
                        b = best.get(g["key"])
                        st.markdown(f'<div class="panel gcard"><div class="qtext">{g["icon"]} {esc(g["name"])}</div>'
                                    f'<div class="small">{esc(g["desc"])}</div>'
                                    f'<div class="qmeta">{("🏅 Rekordingiz: " + str(b)) if b is not None else ("😎 XP yo‘q" if not g["reward"] else "Hali o‘ynalmagan")}</div></div>',
                                    unsafe_allow_html=True)
                        st.button("▶️ O‘ynash", key=f"gp_{g['key']}", on_click=start, args=(g["key"],))
    with tabs[-1]:
        names = {g["key"]: f"{g['icon']} {g['name']}" for g in GAMES if g["reward"]}
        pick = st.selectbox("O‘yin", list(names), format_func=lambda k: names[k], key="gm_rec_pick")
        top = K.game_top(pick, 10)
        if top:
            H["table"]([{"O‘rin": i + 1, "Ism": f"{r['avatar'] or ''} {r['name']}", "Eng yaxshi ball": r["score"], "O‘yinlar": r["plays"]}
                        for i, r in enumerate(top)])
        else:
            st.info("Bu o‘yinda hali natija yo‘q. Birinchi bo‘ling!")
