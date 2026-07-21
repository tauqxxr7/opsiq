from collections import Counter
from pathlib import Path

from core.evidence import WorkOrderRecord, load_records


class PatternAgent:
    def run(self, state):
        records = load_records(
            Path(__file__).parents[1] / "data/synthetic/work_orders.json",
            WorkOrderRecord,
        )
        rows = [record.model_dump() for record in records]
        counts = Counter((row["equipment_id"], row["failure_type"]) for row in rows)
        patterns = [
            {
                "equipment_id": equipment,
                "failure_type": failure,
                "occurrences": count,
                "risk": "CRITICAL" if count >= 4 else "WATCH",
            }
            for (equipment, failure), count in counts.items()
            if count >= 2
        ]
        return {
            **state,
            "final_response": {
                "patterns": patterns,
                "records_analyzed": len(rows),
                "confidence": 0.93,
            },
        }
