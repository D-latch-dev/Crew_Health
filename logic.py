"""Status logic: compare readings with the crew member's own baseline."""
TOL = {"hr": 8, "sys": 10, "dia": 8, "temp": 0.4, "sleep": 1.0}


def assess(value, baseline, key):
    if value is None:
        return "No data", "off"
    d = value - baseline
    if abs(d) <= TOL[key]:
        return "Near baseline", "ok"
    return ("Above baseline" if d > 0 else "Below baseline"), "warn"


def assess_bp(sys_, dia, base):
    if sys_ is None or dia is None:
        return "No data", "off"
    a, b = assess(sys_, base["sys"], "sys"), assess(dia, base["dia"], "dia")
    return a if a[1] == "warn" else b


def sleep_headline(hours, base):
    if hours is None:
        return "Log your sleep to see your trend", "no readings yet", "off"
    gap = base["sleep"] - hours
    if gap > TOL["sleep"]:
        return "Sleep is below your baseline", f"{gap:.1f} h below baseline", "warn"
    return "Sleep is near your baseline", "within your usual range", "ok"
