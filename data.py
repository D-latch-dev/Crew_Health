"""Illustrative mission data. Swap for real sensor/log inputs."""
MISSION_DAY = 128
BASELINE = {"hr": 62, "sys": 116, "dia": 74, "glu": 90, "temp": 36.6, "sleep": 7.2}
LATEST = {"hr": 64, "sys": 118, "dia": 76, "glu": 92, "temp": 36.7}
DAYS = list(range(122, 129))
SERIES = {
    "Sleep (h)": [7.1, 6.8, 7.3, 6.4, 6.1, 5.9, 5.8],
    "Heart rate (bpm)": [62, 63, 62, 64, 63, 65, 64],
    "Temperature (°C)": [36.6, 36.6, 36.7, 36.6, 36.7, 36.7, 36.7],
}
BASE_BY_SERIES = {"Sleep (h)": 7.2, "Heart rate (bpm)": 62, "Temperature (°C)": 36.6}
LOG = [
    {"Day": 128, "Type": "Heart rate", "Value": "64 bpm", "Note": "Resting"},
    {"Day": 128, "Type": "Glucose", "Value": "92 mg/dL", "Note": "Fasting, manual entry"},
    {"Day": 127, "Type": "Sleep", "Value": "5.9 h", "Note": "Woke twice"},
]
