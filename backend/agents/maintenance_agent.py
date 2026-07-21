from pathlib import Path

from core.evidence import WorkOrderRecord, load_records


class MaintenanceAgent:
    def run(self, state):
        rows = load_records(
            Path(__file__).parents[1] / "data/synthetic/work_orders.json",
            WorkOrderRecord,
        )
        equipment = (state.get("equipment_id") or "").strip().upper()
        history = [row.model_dump() for row in rows if row.equipment_id.upper() == equipment]
        if not history:
            response = {
                "status": "no_data",
                "message": f"No maintenance records found for {equipment}.",
                "evidence": [],
                "limitations": ["Analysis is limited to the loaded synthetic work-order dataset."],
            }
        else:
            response = {
                "equipment_id": equipment,
                "risk_level": "CRITICAL" if len(history) >= 4 else "MONITOR",
                "history": history,
                "confidence": 0.88,
            }
        return {**state, "final_response": response}
