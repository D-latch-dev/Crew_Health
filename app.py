"""Crew Health - personal health monitor (NASA Space Apps 2026 demo).
Run:  pip install -r requirements.txt  &&  streamlit run app.py
Accounts and readings are stored locally in crew_health.db.
Decision support only. Not a diagnosis or treatment recommendation."""
import pandas as pd
import streamlit as st

import body
import components as C
import db
import logic as L
from styles import inject

ENV = {
    "Spacecraft": "Reduced gravity: follow prescribed exercise. A closed cabin still requires separate environmental monitoring.",
    "Space station": "Microgravity in a shared habitat: keep exercise on schedule and report air or water concerns through station channels.",
    "Rover": "Confined cabin and long drives: watch fatigue and hydration, and plan rest between sorties.",
    "Planet / moon base": "Partial gravity, dust and radiation: protect eyes and lungs, keep bone-loading exercise, follow habitat monitoring.",
}
st.set_page_config(page_title="Crew Health", page_icon="🛰️", layout="wide", initial_sidebar_state="collapsed")
inject()
db.init()
S = st.session_state


# ---------------- Sign up / log in ----------------
def auth():
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div class="brand" style="margin-top:6vh">CREW HEALTH</div>'
                    '<div class="mut" style="margin-bottom:14px">Personal health monitor · your data stays onboard</div>',
                    unsafe_allow_html=True)
        t1, t2 = st.tabs(["Log in", "Sign up"])
        with t1:
            em = st.text_input("Email", key="li_e")
            pw = st.text_input("Password", type="password", key="li_p")
            if st.button("Log in", type="primary", use_container_width=True):
                u = db.login(em, pw)
                if u:
                    S.user = u
                    st.rerun()
                st.error("Email or password is incorrect.")
        with t2:
            name = st.text_input("Full name")
            crew = st.text_input("Crew ID (optional)")
            em2 = st.text_input("Email", key="su_e")
            p1 = st.text_input("Password (8+ characters)", type="password", key="su_p")
            p2 = st.text_input("Confirm password", type="password", key="su_p2")
            day = st.number_input("Mission day today", 1, 3000, 1)
            with st.expander("Preflight baseline (optional, edit if you know yours)"):
                b = db.DEF_BASE
                c = st.columns(3)
                base = dict(
                    hr=c[0].number_input("Heart rate (bpm)", 30, 120, b["hr"]),
                    sys=c[1].number_input("Systolic (mmHg)", 70, 200, b["sys"]),
                    dia=c[2].number_input("Diastolic (mmHg)", 40, 130, b["dia"]),
                    glu=c[0].number_input("Glucose (mg/dL)", 50, 250, b["glu"]),
                    temp=c[1].number_input("Temp (°C)", 35.0, 39.0, b["temp"], step=0.1),
                    sleep=c[2].number_input("Sleep (h)", 3.0, 12.0, b["sleep"], step=0.1))
            ok = st.checkbox("I understand this tool is decision support, not a diagnosis.")
            if st.button("Create account", type="primary", use_container_width=True):
                if not (name.strip() and "@" in em2):
                    st.error("Enter your name and a valid email.")
                elif len(p1) < 8 or p1 != p2:
                    st.error("Password must be 8+ characters and match the confirmation.")
                elif not ok:
                    st.error("Please accept the notice to continue.")
                else:
                    uid = db.signup(em2, name, crew, p1, day, base)
                    if uid:
                        S.user = db.user(uid)
                        st.rerun()
                    st.error("That email is already registered. Try logging in.")
    st.stop()


if "user" not in S:
    auth()

U = S.user
uid, B, DAY = U["id"], U["base"], db.mission_day(U)
N = {k: db.latest(uid, k) for k in db.METRICS}
mood = db.mood_today(uid, DAY)
dn = db.done_set(uid, DAY)
fmt = lambda x: "—" if x is None else f"{x:g}"

tasks = [dict(t="Morning vitals logged", when="today", done=db.has_today(uid, DAY, ("hr", "sys"))),
         dict(t="Nutrition log complete", when="today", done="nutrition" in dn),
         dict(t="Mood & symptom check-in", when="today", done=bool(mood)),
         dict(t="Prescribed exercise session", when="scheduled today", done="exercise" in dn or db.has_today(uid, DAY, ("ex",)))]
pts = 20 * sum(t["done"] for t in tasks)

with st.sidebar:
    st.markdown(f"**{U['name']}**  \n{U['crew_id'] or 'No crew ID'} · Mission day {DAY}")
    if st.button("Load 7 days of demo data", use_container_width=True):
        db.seed_demo(uid, DAY)
        st.rerun()
    if st.button("Log out", use_container_width=True):
        del S["user"]
        st.rerun()
    st.caption("")

C.header(DAY, db.count(uid), U["name"])
tabs = st.tabs(["Overview", "Health log", "Trends", "Care protocols", "Medical support"])

KINDS = {"Heart rate": ("hr", "bpm", 20, 220, 1), "Blood glucose": ("glu", "mg/dL", 30, 400, 1),
         "Temperature": ("temp", "°C", 34.0, 42.0, 0.1), "Sleep": ("sleep", "hours", 0.0, 16.0, 0.1),
         "Exercise": ("ex", "minutes", 0, 600, 1)}


@st.dialog("Log a reading", width="large")
def log_dialog():
    kind = st.selectbox("Reading", ["Blood pressure", *KINDS])
    m1, m2 = st.columns([1, 1.15])
    if kind == "Blood pressure":
        m1.markdown("""**Blood pressure · manual entry**

<span class="mut" style="text-transform:none;letter-spacing:0;font-size:13px">Systolic (upper) over diastolic (lower).<br><br>1 &nbsp;Rest as directed by your mission protocol.<br>2 &nbsp;Secure your body and support the cuffed arm as trained.<br>3 &nbsp;Fit the approved cuff; stay still and quiet while measuring.</span>""",
                    unsafe_allow_html=True)
    else:
        m1.markdown('<span class="mut" style="text-transform:none;letter-spacing:0;font-size:13px">Use your approved device and mission-specific measurement procedure.</span>',
                    unsafe_allow_html=True)
    with m2:
        if kind == "Blood pressure":
            f = st.columns(2)
            sy = f[0].number_input("Systolic", 60, 250, value=None, placeholder="— mmHg")
            di = f[1].number_input("Diastolic", 30, 160, value=None, placeholder="— mmHg")
        else:
            key, unit, lo, hi, step = KINDS[kind]
            val = st.number_input(f"{kind} ({unit})", lo, hi, value=None, step=step, placeholder=f"— {unit}")
        note = st.text_input("Context / notes (optional)", placeholder="e.g., after exercise or a repeat reading")
        if st.button("Save reading", type="primary", use_container_width=True):
            if kind == "Blood pressure":
                if sy and di and sy > di:
                    db.add(uid, DAY, "sys", float(sy), note)
                    db.add(uid, DAY, "dia", float(di), note)
                    st.rerun()
                st.warning("Enter both numbers (systolic must be higher than diastolic).")
            elif val is not None:
                db.add(uid, DAY, key, float(val), note)
                st.rerun()
            else:
                st.warning("Enter a value first.")
        st.markdown('<div class="warn" style="font-size:12px">Outside your mission limits or feeling unwell? Follow your escalation protocol.</div>',
                    unsafe_allow_html=True)


# ---------------- Overview ----------------
with tabs[0]:
    h1, h2, h3 = st.columns([2.3, 3.6, 1.3], vertical_alignment="center")
    h1.markdown('<div class="eyebrow">MONITOR / ASSESS / ACT</div><h1 class="hero">Your health, at a glance</h1>',
                unsafe_allow_html=True)
    env = h2.segmented_control("Mission environment", list(ENV), default="Spacecraft",
                               label_visibility="collapsed", help="Mission environment (demo context)") or "Spacecraft"
    if h3.button("+  Log a reading", type="primary", use_container_width=True):
        log_dialog()

    sleep_st = L.assess(N["sleep"], B["sleep"], "sleep")
    cv_warn = "warn" in (L.assess(N["hr"], B["hr"], "hr")[1], L.assess_bp(N["sys"], N["dia"], B)[1])
    left, right = st.columns([1.65, 1])
    with left, st.container(border=True):
        st.markdown("#### Understand your body")
        body.render(sleep_st[1] == "warn", bool(mood), cv_warn, int(N["hr"] or B["hr"]), height=300)
        st.caption(f"{env.upper()} CONTEXT · {ENV[env]}")
    with right, st.container(border=True):
        C.routine(tasks, pts, 80, db.streak(uid, DAY))
        b1, b2 = st.columns(2)
        if not tasks[1]["done"] and b1.button("Nutrition done", use_container_width=True):
            db.mark(uid, DAY, "nutrition")
            st.rerun()
        if not tasks[3]["done"] and b2.button("Exercise done", use_container_width=True):
            db.mark(uid, DAY, "exercise")
            st.rerun()

    st.markdown('**Health indicators** <span class="mut" style="text-transform:none;letter-spacing:0">· compared with your preflight baseline</span>',
                unsafe_allow_html=True)
    c = st.columns(6)
    bp = "—" if N["sys"] is None or N["dia"] is None else f"{N['sys']:g}/{N['dia']:g}"
    C.indicator(c[0], "Heart rate", fmt(N["hr"]), "bpm", f"Baseline {B['hr']} bpm", *L.assess(N["hr"], B["hr"], "hr"))
    C.indicator(c[1], "Blood pressure", bp, "mmHg", f"Baseline {B['sys']}/{B['dia']}", *L.assess_bp(N["sys"], N["dia"], B))
    C.indicator(c[2], "Blood glucose", fmt(N["glu"]), "mg/dL", "Fasting · manual entry",
                *(("Review context", "ok") if N["glu"] is not None else ("No data", "off")))
    C.indicator(c[3], "Temperature", fmt(N["temp"]), "°C", f"Baseline {B['temp']} °C", *L.assess(N["temp"], B["temp"], "temp"))
    C.indicator(c[4], "Sleep", fmt(N["sleep"]), "hours", f"Baseline {B['sleep']} hours", *sleep_st)
    if mood:
        C.indicator(c[5], "Mood", mood, "", "Daily self-report", "Logged", "ok")
    else:
        C.indicator(c[5], "Mood", "Not logged", "", "Daily self-report", "Check-in due", "warn")

    l2, r2 = st.columns([1.55, 1])
    with l2, st.container(border=True):
        sl = db.series(uid, "sleep", 7)
        title, delta, tone = L.sleep_headline(N["sleep"], B)
        st.markdown(f'#### {title} &nbsp; <span class="big" style="font-size:22px">{fmt(N["sleep"])} h</span> '
                    f'<span class="{tone}" style="font-size:13px">{delta}</span>', unsafe_allow_html=True)
        if sl:
            vals = [v for _, v in sl]
            C.chart([d for d, _ in sl], vals, B["sleep"], hi=max(8.5, max(vals) + 0.5),
                    highlight_last=vals[-1] < B["sleep"] - 1)
        else:
            st.info("No sleep logged yet. Use “+ Log a reading” to add your first night.")
        st.caption(f"A change worth checking in on, not a diagnosis · mission day · preflight baseline {B['sleep']} h")
    with r2, st.container(border=True):
        st.markdown("#### Daily check-in")
        st.caption("How are you feeling today? About 1 min.")
        for col, (n, lab) in zip(st.columns(4), db.MOODS.items()):
            if col.button(lab, key=f"m_{lab}", type="primary" if S.get("mood") == n else "secondary", use_container_width=True):
                S.mood = n
                st.rerun()
        if st.button("Start check-in  →", type="primary", use_container_width=True):
            if S.get("mood"):
                db.add(uid, DAY, "mood", float(S.mood), db.MOODS[S.mood])
                S.mood = None
                st.rerun()
            st.warning("Select how you feel first.")
        st.caption(f"Selected: {db.MOODS[S.mood]}. Private by default." if S.get("mood") else "Nothing selected yet. Private by default.")

    st.markdown('**Next steps** <span class="mut" style="text-transform:none;letter-spacing:0">· guidance supports—not replaces—your mission medical protocols (hover for details)</span>',
                unsafe_allow_html=True)
    s = st.columns(3)
    warn = sleep_st[1] == "warn"
    C.step(s[0], "01 / FOLLOW UP" if warn else "01 / KEEP IT UP", "warn" if warn else "ok",
           "Review your sleep" if warn else "Keep your sleep steady",
           "Sleep is below your baseline. Log symptoms and review your approved sleep and fatigue protocol." if warn
           else "Keep a fixed sleep window and log each night so changes show up early.", "Sleep protocol")
    C.step(s[1], "02 / KEEP TRACK", "ok", "Complete your health log",
           "Add mood and any new symptoms. Record exercise and nutrition to give your readings more context.", "Health log")
    C.step(s[2], "03 / GET SUPPORT", "ok", "Know when to escalate",
           "New or severe symptoms? Follow onboard emergency procedures. Ground replies may be delayed.", "Medical support")
    C.html('<div class="foot"><span>Not a diagnosis or treatment recommendation.</span>'
           '<span>Unmeasured risks still require scheduled mission screening.</span></div>')

# ---------------- Health log ----------------
with tabs[1]:
    st.markdown("### Health log")
    with st.form("add"):
        f = st.columns([3, 1], vertical_alignment="bottom")
        sym = f[0].text_input("Add a symptom or note")
        if f[1].form_submit_button("Add to log", use_container_width=True) and sym.strip():
            db.add(uid, DAY, "symptom", None, sym.strip())
            st.rerun()
    rows = db.log(uid)
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.download_button("Download my records (CSV)", pd.DataFrame(rows).to_csv(index=False), "crew_health_records.csv")
    else:
        st.info("No records yet. Use “+ Log a reading” on the Overview tab.")

# ---------------- Trends ----------------
with tabs[2]:
    st.markdown("### Trends")
    opts = {"Sleep (h)": "sleep", "Heart rate (bpm)": "hr", "Systolic BP (mmHg)": "sys", "Temperature (°C)": "temp", "Glucose (mg/dL)": "glu"}
    pick = st.selectbox("Indicator", list(opts))
    sr = db.series(uid, opts[pick], 14)
    if len(sr) < 2:
        st.info("Log this indicator on at least two different days to see a trend.")
    else:
        v = [x for _, x in sr]
        lo, hi = min(v + [B[opts[pick]]]), max(v + [B[opts[pick]]])
        pad = (hi - lo) * 0.3 or 1
        C.chart([d for d, _ in sr], v, B[opts[pick]], kind="line", lo=lo - pad, hi=hi + pad, ticks=(round(lo, 1), round(hi, 1)))

# ---------------- Care protocols ----------------
with tabs[3]:
    st.markdown("### Care protocols")
    st.caption("Placeholder content. Replace with your mission-approved protocols.")
    for t, txt in {"Sleep and fatigue": "Keep a fixed sleep window, dim lights before sleep, limit caffeine, log symptoms.",
                   "Exercise countermeasures": "Complete scheduled resistive and aerobic sessions to protect bone and muscle.",
                   "Mood and isolation": "Keep regular contact with family and the behavioral health team."}.items():
        with st.expander(t):
            st.write(txt)

# ---------------- Medical support ----------------
with tabs[4]:
    st.markdown("### Medical support")
    st.error("New or severe symptoms: follow onboard emergency procedures first.")
    st.info("Ground replies may be delayed. Send your health log and wait for guidance while following your protocol.")
