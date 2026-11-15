"""Illustrative body view with status call-outs (matches the 'Understand your body' card).
Subtle motion only: breathing outline, pulsing status dots. Not a live signal."""
import json

import streamlit.components.v1 as components

PAGE = """
<style>
body{margin:0;background:transparent}
svg{width:100%;height:auto;display:block;font-family:Inter,system-ui,sans-serif}
.eb{font-size:10.5px;letter-spacing:.08em}.tt{font-size:19px;font-weight:600}.ds{font-size:13px;fill:#8a9aa3}
.lg{font-size:11px;fill:#9bb0b8}
#fig{transform-box:fill-box;transform-origin:50% 40%;animation:br 5s ease-in-out infinite}
.pulse{transform-box:fill-box;transform-origin:center;animation:pl 2.4s ease-in-out infinite}
.beat{transform-box:fill-box;transform-origin:center;animation:bt __DUR__s ease-in-out infinite}
@keyframes br{0%,100%{transform:scale(1)}50%{transform:scale(1.015)}}
@keyframes pl{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.5);opacity:.45}}
@keyframes bt{0%,100%{transform:scale(1)}12%{transform:scale(1.5)}24%{transform:scale(1)}36%{transform:scale(1.25)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>
<svg viewBox="0 0 700 322" role="img" aria-label="Illustrative body view with status call-outs">
 <g id="fig" fill="rgba(155,232,207,.16)" stroke="#5fb3a2" stroke-width="1.5" stroke-linejoin="round">
  <ellipse cx="350" cy="38" rx="14" ry="18"/><path d="M343 54V66H357V54"/>
  <path d="M318 74Q350 64 382 74L388 150Q388 170 380 182H320Q312 170 312 150Z"/>
  <path d="M318 76Q298 82 296 110L286 196L298 198L312 120L322 100Z"/>
  <path d="M382 76Q402 82 404 110L414 196L402 198L388 120L378 100Z"/>
  <path d="M320 180H349L345 282H331Z"/><path d="M351 180H380L369 282H355Z"/>
 </g>
 <line id="l1" x1="200" y1="34" x2="342" y2="34" stroke-width="1.2"/>
 <circle id="d1" class="pulse" cx="350" cy="34" r="7"/>
 <line id="l2" x1="367" y1="112" x2="462" y2="112" stroke-width="1.2"/>
 <circle id="d2" class="beat" cx="360" cy="112" r="7"/>
 <text id="e1" class="eb" x="20" y="38">SLEEP &amp; MOOD</text><text id="t1" class="tt" x="20" y="66"></text>
 <text id="a1" class="ds" x="20" y="92"></text><text id="b1" class="ds" x="20" y="110"></text>
 <text id="e2" class="eb" x="480" y="38">CARDIOVASCULAR</text><text id="t2" class="tt" x="480" y="66"></text>
 <text id="a2" class="ds" x="480" y="92"></text><text id="b2" class="ds" x="480" y="110"></text>
 <text class="eb" x="480" y="176" fill="#cfe0e5">BONE &amp; IMMUNE HEALTH</text>
 <text class="tt" x="480" y="204" fill="#e6eef0">Not assessed here</text>
 <text class="ds" x="480" y="230">Keep scheduled screenings;</text><text class="ds" x="480" y="248">these readings cannot rule out risk.</text>
 <line x1="20" y1="294" x2="680" y2="294" stroke="#1b3340"/>
 <circle cx="26" cy="308" r="4" fill="#9be8cf"/><text class="lg" x="38" y="312">Near baseline</text>
 <circle cx="156" cy="308" r="4" fill="#f5c97f"/><text class="lg" x="168" y="312">Follow up</text>
 <circle cx="270" cy="308" r="4" fill="none" stroke="#8a9aa3"/><text class="lg" x="282" y="312">Not assessed</text>
 <text class="lg" x="680" y="312" text-anchor="end">Motion is illustrative, not a live signal.</text>
</svg>
<script>
const D=__DATA__,C={ok:"#9be8cf",warn:"#f5c97f"},$=i=>document.getElementById(i);
[["1","sleep"],["2","cv"]].forEach(([n,k])=>{const d=D[k],c=C[d.tone];
 ["e","t"].forEach(p=>$(p+n).setAttribute("fill",c));$("t"+n).textContent=d.title;
 $("a"+n).textContent=d.l1;$("b"+n).textContent=d.l2;$("d"+n).setAttribute("fill",c);$("l"+n).setAttribute("stroke",c)});
</script>
"""


def _card(tone, ok_lines, warn_title, warn_lines):
    return dict(tone="ok", title="Near baseline", l1=ok_lines[0], l2=ok_lines[1]) if tone == "ok" else \
        dict(tone="warn", title=warn_title, l1=warn_lines[0], l2=warn_lines[1])


def render(sleep_warn, mood_logged, cv_warn, hr, height=340):
    if sleep_warn:
        sleep = dict(tone="warn", title="Follow up", l1="Sleep is below baseline.",
                     l2="Complete your mood check-in." if not mood_logged else "Mood check-in logged.")
    elif not mood_logged:
        sleep = dict(tone="warn", title="Follow up", l1="Sleep looks steady.", l2="Complete your mood check-in.")
    else:
        sleep = dict(tone="ok", title="Near baseline", l1="Sleep and mood check-ins", l2="look steady.")
    cv = _card("warn" if cv_warn else "ok", ("Heart rate and blood pressure", "are close to your baseline."),
               "Follow up", ("Heart rate or blood pressure", "differs from your baseline."))
    page = PAGE.replace("__DATA__", json.dumps(dict(sleep=sleep, cv=cv))).replace("__DUR__", f"{60 / hr:.2f}")
    components.html(page, height=height, scrolling=False)
