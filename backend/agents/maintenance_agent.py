from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import mean

from core.evidence import WorkOrderRecord, dataset_sha256, deterministic_analysis_id, load_records
from core.methodology import MAINTENANCE_METHODOLOGY_VERSION

DATA_PATH = Path(__file__).parents[1] / "data/synthetic/work_orders.json"
SEVERITY = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
WEIGHTS = {"recurrence_frequency": 25, "recent_incidents": 20, "severity": 20, "downtime_burden": 15, "repeated_root_cause": 10, "shrinking_failure_intervals": 10}


def _date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        return 1.0
    index = (len(ordered) - 1) * fraction
    lower, upper = int(index), min(int(index) + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


class MaintenanceAgent:
    def __init__(self, records=None, data_path=DATA_PATH):
        self._records_override = records
        self.data_path = Path(data_path)

    def _records(self):
        return self._records_override if self._records_override is not None else load_records(self.data_path, WorkOrderRecord)

    def analyze(self, equipment_id):
        records = self._records()
        rows = [row.model_dump() if hasattr(row, "model_dump") else row for row in records]
        equipment = equipment_id.strip().upper()
        dataset_hash = dataset_sha256(self.data_path) if self._records_override is None else deterministic_analysis_id("fixture", {"rows": rows}, "fixture", "v1")
        analysis_id = deterministic_analysis_id("maintenance", {"equipment_id": equipment}, dataset_hash, MAINTENANCE_METHODOLOGY_VERSION)
        metadata = {"analysis_id": analysis_id, "dataset_hash": dataset_hash, "methodology_version": MAINTENANCE_METHODOLOGY_VERSION, "generated_at": datetime.now(timezone.utc).isoformat(), "synthetic_data": True}
        history = [row for row in rows if row["equipment_id"].upper() == equipment]
        if not history:
            return {"status": "no_data", "message": f"No maintenance records found for {equipment}.", "evidence": [], "limitations": ["Analysis is limited to the loaded synthetic work-order dataset."], "metadata": metadata}

        latest = max(value for row in rows if (value := _date(row.get("date"))))
        dated = sorted((value, row) for row in history if (value := _date(row.get("date"))))
        dates = [value for value, _ in dated]
        intervals = [(right-left).days for left, right in zip(dates, dates[1:])]
        failure_counts = Counter(row["failure_type"] for row in history)
        cause_counts = Counter(row["root_cause"] for row in history)
        dominant_failure, failure_count = failure_counts.most_common(1)[0]
        dominant_cause, cause_count = cause_counts.most_common(1)[0]
        buckets = {"0_90": 0, "91_180": 0, "181_365": 0}
        for event_date, _ in dated:
            age = (latest-event_date).days
            if 0 <= age <= 90: buckets["0_90"] += 1
            elif age <= 180: buckets["91_180"] += 1
            elif age <= 365: buckets["181_365"] += 1
        severities = [SEVERITY.get(row["severity"].upper(), 0) for row in history]
        avg_downtime = mean(float(row["downtime_hours"]) for row in history)
        baseline = _percentile([float(row["downtime_hours"]) for row in rows], .9)
        shrinking = len(intervals) >= 2 and intervals[-1] < mean(intervals[:-1]) * .9
        components = {
            "recurrence_frequency": min(max(failure_count-1, 0)/3, 1)*25,
            "recent_incidents": min((buckets["0_90"] + .6*buckets["91_180"] + .3*buckets["181_365"])/3, 1)*20,
            "severity": (mean(severities)/4)*20,
            "downtime_burden": min(avg_downtime/max(baseline, .01), 1)*15,
            "repeated_root_cause": min(max(cause_count-1, 0)/3, 1)*10,
            "shrinking_failure_intervals": 10 if shrinking else 0,
        }
        breakdown = {name: {"score": round(score, 2), "weight": WEIGHTS[name], "normalized": round(score/WEIGHTS[name], 3), "evidence": self._component_evidence(name, failure_count, cause_count, buckets, severities, avg_downtime, baseline, intervals)} for name, score in components.items()}
        score = round(sum(item["score"] for item in breakdown.values()), 2)
        level = "CRITICAL" if score >= 75 else "HIGH" if score >= 55 else "MONITOR" if score >= 30 else "LOW"
        evidence = [{"record_id": row["work_order_id"], "date": row["date"], "failure_type": row["failure_type"], "root_cause": row["root_cause"], "severity": row["severity"], "downtime_hours": row["downtime_hours"]} for row in history]
        completeness = mean(sum(row.get(field) not in (None, "") for field in ("date", "failure_type", "root_cause", "severity", "downtime_hours"))/5 for row in history)
        confidence = round(.4*min(len(history)/5, 1)+.2*(len(dates)/len(history))+.2*int(bool(cause_counts))+.2*completeness, 2)
        return {"status": "ok", "equipment_id": equipment, "risk_level": level, "risk_score": score, "risk_breakdown": breakdown, "dominant_failure_mode": dominant_failure, "dominant_root_cause": dominant_cause, "recurrence": {"record_count": len(history), "dominant_failure_count": failure_count, "dominant_root_cause_count": cause_count, "recent_buckets": buckets, "interval_days": intervals, "mean_time_between_failures_days": round(mean(intervals),1) if intervals else None, "trend": "SHRINKING" if shrinking else "STABLE" if len(intervals)>=2 else "INSUFFICIENT_HISTORY"}, "confidence": confidence, "evidence": evidence, "supporting_evidence_ids": [item["record_id"] for item in evidence], "methodology": {"name": "deterministic six-component recurrence-risk score", "weights": WEIGHTS, "reference_date": latest.isoformat(), "downtime_baseline": {"type": "dataset_p90", "hours": round(baseline, 2)}}, "limitations": ["This is deterministic historical recurrence-risk analytics, not a trained failure prediction.", "No failure date or fixed component is predicted."], "metadata": metadata}

    @staticmethod
    def _component_evidence(name, failure_count, cause_count, buckets, severities, avg_downtime, baseline, intervals):
        values = {"recurrence_frequency": {"dominant_failure_count": failure_count}, "recent_incidents": buckets, "severity": {"mean_ordinal_severity": round(mean(severities), 2)}, "downtime_burden": {"average_hours": round(avg_downtime, 2), "dataset_p90_hours": round(baseline, 2)}, "repeated_root_cause": {"dominant_root_cause_count": cause_count}, "shrinking_failure_intervals": {"interval_days": intervals}}
        return values[name]

    def catalog(self):
        records = self._records()
        equipment_ids = sorted({(row.equipment_id if hasattr(row, "equipment_id") else row["equipment_id"]).upper() for row in records})
        analyses = [self.analyze(equipment_id) for equipment_id in equipment_ids]
        return {
            "status": "ok" if analyses else "no_data",
            "equipment_count": len(equipment_ids),
            "high_risk_count": sum(item.get("risk_level") in {"HIGH", "CRITICAL"} for item in analyses),
            "equipment": analyses,
        }
    def run(self, state):
        return {**state, "final_response": self.analyze(str(state.get("equipment_id") or ""))}
