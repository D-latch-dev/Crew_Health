import matplotlib.pyplot as plt
import streamlit as st


def html(s):
    st.markdown(s, unsafe_allow_html=True)


def header(day, pending, name="CREW MEMBER 01"):
    import html as _h
    name = _h.escape(name.upper())
    html(f"""<div class="top"><div style="display:flex;gap:28px;align-items:center">
      <span class="brand">CREW HEALTH</span><span class="mut">Personal health monitor</span></div>
      <div style="display:flex;gap:24px;align-items:center"><span class="pill">● Onboard · offline</span>
      <div><b style="font-size:13px">{name}</b><br><span class="mut" style="text-transform:none">Private health view</span></div></div></div>
      <div class="sub"><b style="color:#e6eef0">MISSION DAY {day}</b><span>Long-duration mission</span>
      <span>Local time 08:42</span><span>Your data stays onboard.</span><span>Sync pending · {pending} records</span></div>""")


def indicator(col, label, value, unit, note, status, tone):
    small = "s" if len(value) > 7 else ""
    col.markdown(f"""<div class="ind"><div class="l">{label}</div>
      <div class="v {small}">{value} <span class="u">{unit}</span></div>
      <div class="n">{note}</div><div class="st {tone}">{status}</div></div>""", unsafe_allow_html=True)


def step(col, n, tone, title, body, link):
    col.markdown(f"""<div class="step" title="{body}"><div class="e {tone}">{n}</div>
      <div class="sr"><b>{title}</b><span class="go {tone}">{link} →</span></div></div>""", unsafe_allow_html=True)


def chart(days, vals, baseline, kind="bar", lo=0.0, hi=8.5, ticks=(4, 6, 8), highlight_last=True):
    bg = "#0f202a"
    fig, ax = plt.subplots(figsize=(7.2, 1.9))
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    x = list(range(len(vals)))
    if kind == "bar":
        cols = ["#6fa89b"] * len(vals)
        if highlight_last:
            cols[-1] = "#f5c97f"
        ax.bar(x, vals, color=cols, width=0.5)
    else:
        ax.plot(x, vals, color="#9be8cf", lw=2, marker="o")
    ax.axhline(baseline, color="#c9b27a", ls="--", lw=1)
    ax.set_ylim(lo, hi)
    ax.set_yticks(ticks)
    ax.set_xticks(x)
    ax.set_xticklabels(days)
    ax.tick_params(colors="#8a9aa3", labelsize=8, length=0)
    ax.grid(axis="y", color="#1b2f3a", lw=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def routine(tasks, pts, total, streak=0):
    first = next((i for i, t in enumerate(tasks) if not t["done"]), None)
    rows = ""
    for i, t in enumerate(tasks):
        if t["done"]:
            n, sub = '<span class="rn ok">✓</span>', f'<div class="rs ok">{t["when"]} · complete</div>'
        elif i == first:
            n, sub = f'<span class="rn warn">{i+1:02d}</span>', '<div class="rs warn">Due now · +20 points</div>'
        else:
            n, sub = f'<span class="rn">{i+1:02d}</span>', f'<div class="rs">{t["when"]}</div>'
        rows += f'<div class="rt">{n}<div><div>{t["t"]}</div>{sub}</div></div>'
    done = sum(t["done"] for t in tasks)
    html(f"""<div class="routine"><h4>Your mission routine</h4>
      <div style="display:flex;justify-content:space-between;color:#8a9aa3;font-size:14px">
      <span>{done} of {len(tasks)} complete</span><span class="ok" style="font-size:12px">{pts} / {total} points</span></div>
      <div class="bar"><i style="width:{pts / total * 100:.0f}%"></i></div>{rows}
      <div class="ok" style="font-size:12px;font-weight:600;margin-top:10px">{streak}-day routine streak</div>
      <div class="rs">Earn points for logging—not for “good” readings.</div></div>""")
