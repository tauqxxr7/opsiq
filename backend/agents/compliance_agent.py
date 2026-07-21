from datetime import datetime, timezone
from pathlib import Path

from core.evidence import InspectionRecord, dataset_sha256, deterministic_analysis_id, load_records
from core.methodology import COMPLIANCE_METHODOLOGY_VERSION

DATA_PATH = Path(__file__).parents[1] / "data/synthetic/inspection_reports.json"
PRIORITY = {"CRITICAL": 0, "GAP": 1, "COMPLIANT": 2}


class ComplianceAgent:
    def __init__(self, records=None, data_path=DATA_PATH):
        self._records_override = records
        self.data_path = Path(data_path)

    def analyze(self, standard):
        records = self._records_override if self._records_override is not None else load_records(self.data_path, InspectionRecord)
        rows = [row.model_dump() if hasattr(row, "model_dump") else row for row in records]
        requested = standard.strip().upper()
        dataset_hash = dataset_sha256(self.data_path) if self._records_override is None else deterministic_analysis_id("fixture", {"rows": rows}, "fixture", "v1")
        metadata = {"analysis_id": deterministic_analysis_id("compliance", {"standard": requested}, dataset_hash, COMPLIANCE_METHODOLOGY_VERSION), "dataset_hash": dataset_hash, "methodology_version": COMPLIANCE_METHODOLOGY_VERSION, "generated_at": datetime.now(timezone.utc).isoformat(), "synthetic_data": True}
        matrix = [row for row in rows if row["standard"].upper() == requested]
        if not matrix:
            return {"status": "no_data", "message": f"No inspection evidence found for {requested}.", "evidence": [], "limitations": ["The demonstration corpus currently contains only synthetic OISD-118 evidence.", "This prototype is not legal compliance certification."], "metadata": metadata}
        summary = {"compliant": sum(row["status"] == "COMPLIANT" for row in matrix), "gaps": sum(row["status"] == "GAP" for row in matrix), "critical": sum(row["status"] == "CRITICAL" for row in matrix)}
        percentage = round(summary["compliant"] / len(matrix) * 100, 2)
        actions = [{"rank": index, "record_id": row["record_id"], "clause": row.get("clause"), "severity": row["severity"], "remediation": row["remediation"], "evidence_source": row["evidence_source"]} for index, row in enumerate(sorted((item for item in matrix if item["status"] != "COMPLIANT"), key=lambda item: (PRIORITY[item["status"]], item.get("clause", ""))), 1)]
        evidence = [{"record_id": row["record_id"], "clause": row.get("clause"), "requirement": row["requirement"], "status": row["status"], "evidence_source": row["evidence_source"]} for row in matrix]
        return {"status": "ok", "standard": requested, "requirements_checked": len(matrix), "summary": summary, "matrix": matrix, "compliance_percentage": percentage, "corrective_actions": actions, "evidence": evidence, "supporting_evidence_ids": [row["record_id"] for row in matrix], "confidence": 1.0, "methodology": {"name": "record-derived prototype evidence-gap assessment", "formula": "COMPLIANT records / requirements checked × 100", "status_counts_derived_from": "normalized inspection records"}, "limitations": ["This prototype evidence-gap assessment is not legal compliance certification.", "The bundled demonstration corpus contains only synthetic OISD-118 inspection evidence."], "metadata": metadata}

    def run(self, state):
        return {**state, "final_response": self.analyze(str(state.get("standard") or ""))}
