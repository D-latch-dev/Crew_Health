"""SQLite storage: crew accounts (salted PBKDF2 hashes) and per-astronaut health records.
Everything stays in a local file (crew_health.db), matching the 'data stays onboard' idea."""
import datetime as dt
import hashlib
import hmac
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crew_health.db")
METRICS = ("hr", "sys", "dia", "glu", "temp", "sleep", "mood", "ex")
DEF_BASE = dict(hr=62, sys=116, dia=74, glu=90, temp=36.6, sleep=7.2)
LABEL = {"hr": ("Heart rate", "bpm"), "sys": ("Systolic BP", "mmHg"), "dia": ("Diastolic BP", "mmHg"),
         "glu": ("Glucose", "mg/dL"), "temp": ("Temperature", "°C"), "sleep": ("Sleep", "h"),
         "mood": ("Mood", ""), "ex": ("Exercise", "min"), "symptom": ("Symptom", "")}
DEMO = [[62, 118, 76, 36.6, 92, 7.6, 3, 80], [63, 119, 77, 36.6, 94, 7.4, 3, 75], [62, 118, 76, 36.7, 91, 7.5, 3, 78],
        [65, 122, 79, 36.7, 96, 6.9, 2, 60], [67, 125, 80, 36.8, 99, 6.3, 2, 50], [70, 128, 82, 36.9, 104, 5.9, 2, 40],
        [64, 118, 76, 36.7, 92, 5.8, 2, 35]]
MOODS = {1: "Low", 2: "Okay", 3: "Good", 4: "Great"}


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT, crew_id TEXT,
            salt BLOB, pw BLOB, mission_start TEXT, base TEXT, created TEXT);
        CREATE TABLE IF NOT EXISTS readings(id INTEGER PRIMARY KEY, user_id INTEGER, day INTEGER, metric TEXT,
            value REAL, note TEXT, ts TEXT);
        CREATE TABLE IF NOT EXISTS done(user_id INTEGER, day INTEGER, task TEXT, PRIMARY KEY(user_id, day, task));""")


def _hash(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 200_000)


def _user(r):
    return dict(id=r["id"], name=r["name"], crew_id=r["crew_id"], start=r["mission_start"], base=json.loads(r["base"]))


def user(uid):
    with conn() as c:
        return _user(c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone())


def signup(email, name, crew_id, pw, day, base):
    """Returns the new user id, or None if the email is already registered."""
    salt = os.urandom(16)
    start = (dt.date.today() - dt.timedelta(days=int(day) - 1)).isoformat()
    try:
        with conn() as c:
            cur = c.execute("INSERT INTO users(email,name,crew_id,salt,pw,mission_start,base,created) VALUES(?,?,?,?,?,?,?,?)",
                            (email.strip().lower(), name.strip(), crew_id.strip(), salt, _hash(pw, salt), start,
                             json.dumps(base), dt.datetime.now().isoformat()))
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def login(email, pw):
    with conn() as c:
        r = c.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    return _user(r) if r and hmac.compare_digest(r["pw"], _hash(pw, r["salt"])) else None


def mission_day(u):
    return (dt.date.today() - dt.date.fromisoformat(u["start"])).days + 1


def add(uid, day, metric, value, note=""):
    with conn() as c:
        c.execute("INSERT INTO readings(user_id,day,metric,value,note,ts) VALUES(?,?,?,?,?,?)",
                  (uid, day, metric, value, note, dt.datetime.now().isoformat(timespec="minutes")))


def latest(uid, metric):
    with conn() as c:
        r = c.execute("SELECT value FROM readings WHERE user_id=? AND metric=? ORDER BY day DESC, id DESC LIMIT 1",
                      (uid, metric)).fetchone()
    return r["value"] if r else None


def series(uid, metric, n=7):
    with conn() as c:
        rows = c.execute("""SELECT day, value FROM readings WHERE id IN (SELECT MAX(id) FROM readings
            WHERE user_id=? AND metric=? GROUP BY day) ORDER BY day DESC LIMIT ?""", (uid, metric, n)).fetchall()
    return [(r["day"], r["value"]) for r in reversed(rows)]


def has_today(uid, day, metrics):
    q = ",".join("?" * len(metrics))
    with conn() as c:
        return c.execute(f"SELECT 1 FROM readings WHERE user_id=? AND day=? AND metric IN ({q}) LIMIT 1",
                         (uid, day, *metrics)).fetchone() is not None


def mood_today(uid, day):
    with conn() as c:
        r = c.execute("SELECT note FROM readings WHERE user_id=? AND day=? AND metric='mood' ORDER BY id DESC LIMIT 1",
                      (uid, day)).fetchone()
    return r["note"] if r else None


def mark(uid, day, task):
    with conn() as c:
        c.execute("INSERT OR IGNORE INTO done VALUES(?,?,?)", (uid, day, task))


def done_set(uid, day):
    with conn() as c:
        return {r["task"] for r in c.execute("SELECT task FROM done WHERE user_id=? AND day=?", (uid, day))}


def count(uid):
    with conn() as c:
        return c.execute("SELECT COUNT(*) n FROM readings WHERE user_id=?", (uid,)).fetchone()["n"]


def streak(uid, day):
    with conn() as c:
        days = {r["day"] for r in c.execute("SELECT DISTINCT day FROM readings WHERE user_id=?", (uid,))}
    d, n = (day if day in days else day - 1), 0
    while d in days:
        n, d = n + 1, d - 1
    return n


def log(uid):
    out = []
    with conn() as c:
        for r in c.execute("SELECT * FROM readings WHERE user_id=? ORDER BY id DESC", (uid,)):
            name, unit = LABEL.get(r["metric"], (r["metric"], ""))
            val = r["note"] if r["metric"] == "mood" else ("" if r["value"] is None else f"{r['value']:g} {unit}".strip())
            out.append({"Day": r["day"], "Type": name, "Value": val,
                        "Note": "" if r["metric"] == "mood" else (r["note"] or ""), "Recorded": r["ts"]})
    return out


def seed_demo(uid, day):
    for i, row in enumerate(DEMO):
        d = day - 6 + i
        if d >= 1:
            for m, v in zip(METRICS, row):
                add(uid, d, m, v, MOODS[v] if m == "mood" else "Demo data")
