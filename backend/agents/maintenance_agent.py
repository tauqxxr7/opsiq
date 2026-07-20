from collections import Counter
from datetime import date, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from services.evidence_loader import load_json_records


DATA_PATH = Path(__file__).parents[1] / "data/synthetic/work_orders.json"
SEVERITY_WEIGHTS = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
RISK_WEIGHTS = {
    "recurrence_frequency": 25,
    "recent_incidents": 20,
    "severity": 20,
    "downtime_burden": 15,
    "repeated_root_cause": 10,
    "shrinking_failure_intervals": 10,
}


def _parse_date(value: Any) -> date | None:
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _number(value: Any) -> float:
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return 0.0


class MaintenanceAgent:
    def __init__(self, rows: list[dict[str, Any]] | None = None, data_path: str | Path = DATA_PATH):
        self._rows = rows
        self.data_path = Path(data_path)

    def _records(self) -> list[dict[str, Any]]:
        rows = self._rows if self._rows is not None else load_json_records(self.data_path)
        return [row for row in rows if isinstance(row, dict)]

    def analyze(self, equipment_id: str) -> dict[str, Any]:
        all_rows = self._records()
        equipment = equipment_id.strip().upper()
        history = [row for row in all_rows if str(row.get("equipment_id", "")).strip().upper() == equipment]
        dated_dataset = [parsed for row in all_rows if (parsed := _parse_date(row.get("date")))]
        latest_dataset_date = max(dated_dataset) if dated_dataset else None

        if not history:
            return self._no_data(equipment, latest_dataset_date)

        dated_history = sorted(
            ((parsed, row) for row in history if (parsed := _parse_date(row.get("date")))),
            key=lambda item: item[0],
        )
        dates = [item[0] for item in dated_history]
        intervals = [(later - earlier).days for earlier, later in zip(dates, dates[1:])]
        mtbf = round(mean(intervals), 1) if intervals else None
        trend = self._trend(intervals)

        failure_counts = Counter(
            str(row.get("failure_type", "")).strip() for row in history if row.get("failure_type")
        )
        cause_counts = Counter(
            str(row.get("root_cause", "")).strip() for row in history if row.get("root_cause")
        )
        dominant_failure, dominant_failure_count = failure_counts.most_common(1)[0] if failure_counts else ("Unknown", 0)
        dominant_cause, dominant_cause_count = cause_counts.most_common(1)[0] if cause_counts else ("Unknown", 0)

        recent = {
            str(window): sum(
                1
                for parsed, _ in dated_history
                if latest_dataset_date is not None and 0 <= (latest_dataset_date - parsed).days <= window
            )
            for window in (90, 180, 365)
        }
        downtime = [_number(row.get("downtime_hours")) for row in history]
        cumulative_downtime = round(sum(downtime), 1)
        average_downtime = round(mean(downtime), 1) if downtime else 0.0
        severity_values = [
            SEVERITY_WEIGHTS.get(str(row.get("severity", "")).strip().upper(), 0) for row in history
        ]
        severity_weighted_score = sum(severity_values)

        components = {
            "recurrence_frequency": round(min(max(dominant_failure_count - 1, 0) / 3, 1) * 25, 2),
            "recent_incidents": round(
                min((recent["90"] + 0.6 * recent["180"] + 0.3 * recent["365"]) / 3, 1) * 20,
                2,
            ),
            "severity": round((mean(severity_values) / 4 if severity_values else 0) * 20, 2),
            "downtime_burden": round(min(average_downtime / 12, 1) * 15, 2),
            "repeated_root_cause": round(min(max(dominant_cause_count - 1, 0) / 3, 1) * 10, 2),
            "shrinking_failure_intervals": 10.0 if trend == "SHRINKING" else 0.0,
        }
        risk_breakdown = {
            name: {
                "score": score,
                "weight": RISK_WEIGHTS[name],
                "normalized": round(score / RISK_WEIGHTS[name], 3),
            }
            for name, score in components.items()
        }
        risk_score = round(sum(components.values()), 2)
        risk_level = self._risk_level(risk_score)
        confidence = self._confidence(history, len(dates))

        if risk_level == "CRITICAL":
            recurrence_signal = "High recurrence risk based on historical intervals"
        elif risk_level in {"MONITOR", "HIGH"}:
            recurrence_signal = "Elevated recurrence risk"
        else:
            recurrence_signal = "No immediate recurrence signal"

        evidence_ids = [
            str(row.get("wo_id")) for row in history if row.get("wo_id")
        ]
        explanation = (
            f"{equipment} scored {risk_score}/100 from {len(history)} work orders. "
            f"The dominant failure mode '{dominant_failure}' occurred {dominant_failure_count} times; "
            f"the dominant root cause occurred {dominant_cause_count} times; cumulative downtime was "
            f"{cumulative_downtime} hours. This is deterministic recurrence-risk analytics, not a trained prediction."
        )
        return {
            "equipment_id": equipment,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_breakdown": risk_breakdown,
            "predicted_component": dominant_failure,
            "dominant_failure_mode": dominant_failure,
            "dominant_root_cause": dominant_cause,
            "failure_window": recurrence_signal,
            "recurrence_signal": recurrence_signal,
            "history": history,
            "supporting_evidence_ids": evidence_ids,
            "metrics": {
                "total_incident_count": len(history),
                "incidents_last_90_days": recent["90"],
                "incidents_last_180_days": recent["180"],
                "incidents_last_365_days": recent["365"],
                "repeated_failure_mode_frequency": dominant_failure_count,
                "repeated_root_cause_frequency": dominant_cause_count,
                "cumulative_downtime_hours": cumulative_downtime,
                "average_downtime_hours": average_downtime,
                "severity_weighted_incident_score": severity_weighted_score,
                "mean_time_between_failures_days": mtbf,
                "failure_interval_days": intervals,
                "trend_direction": trend,
                "latest_dataset_date": latest_dataset_date.isoformat() if latest_dataset_date else None,
            },
            "confidence": confidence,
            "explanation": explanation,
            "analytics_type": "deterministic recurrence-risk assessment",
            "synthetic_data": True,
            "no_data": False,
        }

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        equipment = state.get("equipment_id") or "P-201"
        return {**state, "final_response": self.analyze(str(equipment))}

    @staticmethod
    def _risk_level(score: float) -> str:
        if score >= 75:
            return "CRITICAL"
        if score >= 55:
            return "HIGH"
        if score >= 30:
            return "MONITOR"
        return "LOW"

    @staticmethod
    def _trend(intervals: list[int]) -> str:
        if len(intervals) < 2:
            return "INSUFFICIENT_HISTORY"
        midpoint = max(1, len(intervals) // 2)
        earlier = mean(intervals[:midpoint])
        later = mean(intervals[midpoint:])
        if later < earlier * 0.9:
            return "SHRINKING"
        if later > earlier * 1.1:
            return "EXPANDING"
        return "STABLE"

    @staticmethod
    def _confidence(history: list[dict[str, Any]], dated_count: int) -> float:
        required = ("date", "failure_type", "root_cause", "severity", "downtime_hours")
        completeness = mean(
            sum(bool(row.get(field) or row.get(field) == 0) for field in required) / len(required)
            for row in history
        )
        volume = min(len(history) / 5, 1)
        dated_fraction = dated_count / len(history)
        return round(min(1.0, 0.15 + 0.45 * volume + 0.25 * dated_fraction + 0.15 * completeness), 2)

    @staticmethod
    def _no_data(equipment: str, latest_dataset_date: date | None) -> dict[str, Any]:
        breakdown = {
            name: {"score": 0.0, "weight": weight, "normalized": 0.0}
            for name, weight in RISK_WEIGHTS.items()
        }
        return {
            "equipment_id": equipment,
            "risk_level": "LOW",
            "risk_score": 0.0,
            "risk_breakdown": breakdown,
            "predicted_component": None,
            "dominant_failure_mode": None,
            "dominant_root_cause": None,
            "failure_window": "No immediate recurrence signal",
            "recurrence_signal": "No immediate recurrence signal",
            "history": [],
            "supporting_evidence_ids": [],
            "metrics": {
                "total_incident_count": 0,
                "incidents_last_90_days": 0,
                "incidents_last_180_days": 0,
                "incidents_last_365_days": 0,
                "repeated_failure_mode_frequency": 0,
                "repeated_root_cause_frequency": 0,
                "cumulative_downtime_hours": 0.0,
                "average_downtime_hours": 0.0,
                "severity_weighted_incident_score": 0,
                "mean_time_between_failures_days": None,
                "failure_interval_days": [],
                "trend_direction": "INSUFFICIENT_HISTORY",
                "latest_dataset_date": latest_dataset_date.isoformat() if latest_dataset_date else None,
            },
            "confidence": 0.0,
            "explanation": f"No work-order evidence is available for equipment {equipment}.",
            "analytics_type": "deterministic recurrence-risk assessment",
            "synthetic_data": True,
            "no_data": True,
            "message": "No evidence available for the requested equipment.",
        }
