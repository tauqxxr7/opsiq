import random
from datetime import datetime, timedelta, timezone

EQUIPMENT_BASELINE = {
    "P-201": {"temperature_c": 72.0, "vibration_mm_s": 2.8, "pressure_bar": 12.0, "rpm": 2950, "oil_level_pct": 85.0, "bearing_temp_c": 65.0},
    "P-202": {"temperature_c": 68.0, "vibration_mm_s": 2.1, "pressure_bar": 11.5, "rpm": 2960, "oil_level_pct": 92.0, "bearing_temp_c": 61.0},
    "P-203": {"temperature_c": 71.0, "vibration_mm_s": 3.2, "pressure_bar": 11.8, "rpm": 2945, "oil_level_pct": 78.0, "bearing_temp_c": 67.0},
    "P-204": {"temperature_c": 65.0, "vibration_mm_s": 1.9, "pressure_bar": 12.2, "rpm": 2970, "oil_level_pct": 90.0, "bearing_temp_c": 58.0},
    "P-205": {"temperature_c": 63.0, "vibration_mm_s": 1.7, "pressure_bar": 12.5, "rpm": 2980, "oil_level_pct": 95.0, "bearing_temp_c": 55.0},
}
ALARM_THRESHOLDS = {
    "temperature_c": {"warning": 75.0, "critical": 85.0},
    "vibration_mm_s": {"warning": 4.5, "critical": 7.0},
    "pressure_bar": {"warning": 10.0, "critical": 8.5},
    "bearing_temp_c": {"warning": 72.0, "critical": 82.0},
    "oil_level_pct": {"warning": 60.0, "critical": 40.0},
}


def _alarms(reading):
    alarms = []
    for parameter, limits in ALARM_THRESHOLDS.items():
        value, low_alarm = reading[parameter], parameter in {"pressure_bar", "oil_level_pct"}
        level = "CRITICAL" if (value < limits["critical"] if low_alarm else value > limits["critical"]) else "WARNING" if (value < limits["warning"] if low_alarm else value > limits["warning"]) else None
        if level:
            alarms.append({"parameter": parameter, "level": level, "value": value, "threshold": limits[level.lower()]})
    return alarms


def generate_live_reading(equipment_id):
    equipment_id = equipment_id.upper()
    baseline = EQUIPMENT_BASELINE.get(equipment_id, EQUIPMENT_BASELINE["P-205"])
    factor = 1.15 if equipment_id == "P-201" else 1.08 if equipment_id == "P-203" else 1.0
    reading = {
        "asset_id": equipment_id, "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "temperature_c": round(baseline["temperature_c"] * factor + random.gauss(0, 1.2), 1),
        "vibration_mm_s": round(baseline["vibration_mm_s"] * factor + random.gauss(0, .3), 2),
        "pressure_bar": round(baseline["pressure_bar"] + random.gauss(0, .4), 1),
        "rpm": int(baseline["rpm"] + random.gauss(0, 15)),
        "oil_level_pct": round(max(0, baseline["oil_level_pct"] + random.gauss(-.1, .5)), 1),
        "bearing_temp_c": round(baseline["bearing_temp_c"] * factor + random.gauss(0, 1), 1),
    }
    reading["alarms"] = _alarms(reading)
    reading["alarm_count"] = len(reading["alarms"])
    reading["health_signal"] = "CRITICAL" if any(a["level"] == "CRITICAL" for a in reading["alarms"]) else "WARNING" if reading["alarms"] else "NORMAL"
    return reading


def generate_historical_trend(equipment_id, hours=24):
    hours, equipment_id = max(1, min(hours, 168)), equipment_id.upper()
    baseline, now = EQUIPMENT_BASELINE.get(equipment_id, EQUIPMENT_BASELINE["P-205"]), datetime.now(timezone.utc)
    rate = .002 if equipment_id == "P-201" else .001
    return [{"timestamp": (now - timedelta(hours=i)).isoformat().replace("+00:00", "Z"), "temperature_c": round(baseline["temperature_c"] * (1 + rate * (hours - i)) + random.gauss(0, .8), 1), "vibration_mm_s": round(baseline["vibration_mm_s"] * (1 + rate * (hours - i)) + random.gauss(0, .2), 2), "bearing_temp_c": round(baseline["bearing_temp_c"] * (1 + rate * (hours - i)) + random.gauss(0, .6), 1)} for i in range(hours, 0, -1)]
