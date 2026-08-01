import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter
from core.evidence import WorkOrderRecord, load_records

router = APIRouter()
DATA_PATH = Path(__file__).parents[1] / "data/synthetic/work_orders.json"


def _orders():
    return [record.model_dump() for record in load_records(DATA_PATH, WorkOrderRecord)]


@router.get("/reliability")
async def reliability():
    grouped = defaultdict(list)
    for order in _orders(): grouped[order["equipment_id"]].append(order)
    metrics = []
    for equipment_id, orders in grouped.items():
        orders.sort(key=lambda item: item["date"])
        downtime = [float(item["downtime_hours"]) for item in orders]
        dates = [datetime.fromisoformat(item["date"]) for item in orders]
        gaps = [(right - left).days for left, right in zip(dates, dates[1:])]
        modes = Counter(item["failure_type"] for item in orders)
        total = sum(downtime)
        metrics.append({"equipment_id": equipment_id, "total_failures": len(orders), "total_downtime_hours": round(total, 1), "mttr_hours": round(statistics.mean(downtime), 1), "mtbf_days": round(statistics.mean(gaps), 1) if gaps else 0, "most_common_failure": modes.most_common(1)[0][0], "critical_failures": sum(item["severity"] == "CRITICAL" for item in orders), "high_failures": sum(item["severity"] == "HIGH" for item in orders), "availability_estimate_pct": round(max(0, 100 - total / (365 * 24) * 100), 2)})
    metrics.sort(key=lambda item: item["total_downtime_hours"], reverse=True)
    mtbf = [item["mtbf_days"] for item in metrics if item["mtbf_days"]]
    return {"fleet_summary": {"total_equipment_analysed": len(metrics), "total_failures": sum(item["total_failures"] for item in metrics), "total_downtime_hours": round(sum(item["total_downtime_hours"] for item in metrics), 1), "fleet_average_mtbf_days": round(statistics.mean(mtbf), 1) if mtbf else 0, "fleet_average_mttr_hours": round(statistics.mean(item["mttr_hours"] for item in metrics), 1), "highest_risk_asset": metrics[0]["equipment_id"] if metrics else "N/A"}, "equipment_metrics": metrics}


@router.get("/downtime/trends")
async def downtime_trends():
    monthly = defaultdict(float)
    for order in _orders(): monthly[order["date"][:7]] += float(order["downtime_hours"])
    return {"monthly_downtime": [{"month": month, "downtime_hours": round(value, 1)} for month, value in sorted(monthly.items())][-12:]}
