from pathlib import Path

from core.evidence import InspectionRecord, load_records


class ComplianceAgent:
    def run(self, state):
        rows = load_records(
            Path(__file__).parents[1] / "data/synthetic/inspection_reports.json",
            InspectionRecord,
        )
        standard = (state.get("standard") or "").strip().upper()
        matches = [row.model_dump() for row in rows if row.standard.upper() == standard]
        if not matches:
            response = {
                "status": "no_data",
                "message": f"No inspection evidence found for {standard}.",
                "evidence": [],
                "limitations": ["The demonstration corpus currently contains only synthetic OISD-118 inspection evidence."],
            }
        else:
            summary = {
                "compliant": sum(row["status"] == "COMPLIANT" for row in matches),
                "gaps": sum(row["status"] == "GAP" for row in matches),
                "critical": sum(row["status"] == "CRITICAL" for row in matches),
            }
            response = {
                "standard": standard,
                "requirements_checked": len(matches),
                "matrix": matches,
                "summary": summary,
                "confidence": 0.9,
            }
        return {**state, "final_response": response}
