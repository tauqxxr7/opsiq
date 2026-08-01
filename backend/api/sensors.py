from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from services.sensor_simulator import ALARM_THRESHOLDS, EQUIPMENT_BASELINE, generate_historical_trend, generate_live_reading

router = APIRouter()


def _require_equipment(equipment_id):
    equipment_id = equipment_id.upper()
    if equipment_id not in EQUIPMENT_BASELINE:
        raise HTTPException(404, f"No simulated telemetry configured for {equipment_id}.")
    return equipment_id


@router.get("/live/{equipment_id}")
async def live(equipment_id: str):
    return generate_live_reading(_require_equipment(equipment_id))


@router.get("/trend/{equipment_id}")
async def trend(equipment_id: str, hours: int = Query(24, ge=1, le=168)):
    equipment_id = _require_equipment(equipment_id)
    return {"equipment_id": equipment_id, "period_hours": hours, "readings": generate_historical_trend(equipment_id, hours), "thresholds": ALARM_THRESHOLDS}


@router.get("/fleet/status")
async def fleet_status():
    readings = [generate_live_reading(equipment_id) for equipment_id in EQUIPMENT_BASELINE]
    equipment = [{"equipment_id": item["asset_id"], **{key: item[key] for key in ("health_signal", "alarm_count", "temperature_c", "vibration_mm_s", "bearing_temp_c", "rpm", "alarms")}} for item in readings]
    counts = {f"{level.lower()}_count": sum(item["health_signal"] == level for item in equipment) for level in ("CRITICAL", "WARNING", "NORMAL")}
    return {"fleet_size": len(equipment), **counts, "equipment": equipment, "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}


@router.get("/alarms/active")
async def active_alarms():
    alarms = []
    for equipment_id in EQUIPMENT_BASELINE:
        reading = generate_live_reading(equipment_id)
        alarms.extend({**alarm, "equipment_id": equipment_id, "timestamp": reading["timestamp"]} for alarm in reading["alarms"])
    alarms.sort(key=lambda alarm: alarm["level"] == "CRITICAL", reverse=True)
    return {"total_alarms": len(alarms), "critical_alarms": sum(alarm["level"] == "CRITICAL" for alarm in alarms), "alarms": alarms}
