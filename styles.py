import streamlit as st

CSS = """
<style>
:root{--card:#0f202a;--line:#1b2f3a;--mint:#9be8cf;--amber:#f5c97f;--ink:#e6eef0;--mut:#8a9aa3}
.block-container{max-width:1240px;padding-top:1.4rem}
header[data-testid="stHeader"]{background:transparent}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.brand{font-size:26px;font-weight:600;letter-spacing:.02em}
.mut{color:var(--mut);font-size:12px;letter-spacing:.06em;text-transform:uppercase}
.pill{background:#0f202a;border-radius:99px;padding:8px 16px;color:var(--mint);font-size:13px}
.sub{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:var(--mut);font-size:12px;
  padding:14px 0;border-top:1px solid var(--line);margin-top:14px}
.eyebrow{color:var(--mint);font-size:11px;letter-spacing:.08em}
h1.hero{font-size:34px;font-weight:600;margin:6px 0 4px}
.lead{color:var(--mut)}
.ind{background:var(--card);border-radius:12px;padding:14px;min-height:140px}
.ind .l{color:var(--mut);font-size:13px}
.ind .v{font-size:30px;font-weight:600;margin:6px 0 0;line-height:1.1}
.ind .v.s{font-size:22px;padding:6px 0}
.ind .n{color:var(--mut);font-size:11px;margin-top:6px}
.ok{color:var(--mint)}.warn{color:var(--amber)}
.ind .st{font-size:11px;margin-top:6px;font-weight:500}
.big{font-size:38px;font-weight:600}
.step{background:var(--card);border-radius:12px;padding:18px;min-height:190px}
.step .e{font-size:10px;letter-spacing:.08em;margin-bottom:10px}
.step h3{margin:0 0 8px;font-size:20px;font-weight:600}
.step p{color:var(--mut);font-size:13px}
.step .go{font-size:13px;font-weight:500;margin-top:18px}
.foot{display:flex;justify-content:space-between;color:var(--mut);font-size:11px;
  border-top:1px solid var(--line);padding-top:14px;margin-top:28px;gap:12px;flex-wrap:wrap}
[data-testid="stVerticalBlockBorderWrapper"]{background:var(--card);border:none;border-radius:14px}
.stButton>button{border-radius:8px;border:1px solid var(--line);background:#12303a;color:var(--ink)}
.stButton>button[kind="primary"]{background:var(--mint);color:#06231b;border:none;font-weight:600}
.stTabs [data-baseweb="tab"]{padding:14px 24px}

.routine h4{margin:0 0 6px;font-size:19px;font-weight:600}
.bar{height:5px;background:#1b3340;border-radius:9px;margin:8px 0 10px}.bar i{display:block;height:100%;background:var(--mint);border-radius:9px}
.rt{display:flex;gap:16px;padding:7px 0;font-size:14px}.rn{width:22px;color:var(--mut);font-size:13px}
.rs{color:var(--mut);font-size:11.5px}.rs.ok,.rn.ok{color:var(--mint)}.rs.warn,.rn.warn{color:var(--amber)}
.ctx{color:var(--mut);font-size:11.5px;margin:10px 0}

.block-container{padding-top:.8rem!important;padding-bottom:1rem!important}
[data-testid="stVerticalBlock"]{gap:.65rem}
[data-testid="stMarkdownContainer"] h4{margin:0;padding:0 0 .2rem;font-size:18px}
.brand{font-size:22px}.sub{padding:8px 0;margin-top:8px}
h1.hero{font-size:26px;margin:2px 0 0}
.ind{padding:10px 12px;min-height:0}.ind .v{font-size:26px;margin:2px 0 0}.ind .v.s{font-size:19px;padding:4px 0}
.ind .u{font-size:12px;color:var(--mut);font-weight:400}.ind .n{margin-top:2px}
.step{padding:10px 14px;min-height:0}.step .e{margin-bottom:4px}
.sr{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:15px}
.step .go{margin:0;font-size:12px;white-space:nowrap}
.stTabs [data-baseweb="tab"]{padding:8px 18px}
.rt{padding:3px 0}.routine h4{font-size:17px}.bar{margin:6px 0}
.foot{margin-top:6px;padding-top:8px}
.off{color:var(--mut)}
.auth{max-width:460px;margin:0 auto}
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)
