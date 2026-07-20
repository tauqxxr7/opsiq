from pathlib import Path
from statistics import mean
from typing import Any

from services.evidence_loader import load_json_records


DATA_PATH = Path(__file__).parents[1] / "data/synthetic/inspection_reports.json"
STATUS_SEVERITY = {"COMPLIANT": "LOW", "GAP": "HIGH", "CRITICAL": "CRITICAL"}
PRIORITY = {"CRITICAL": 0, "GAP": 1, "COMPLIANT": 2}


class ComplianceAgent:
    def __init__(
        self,
        rows: list[dict[str, Any]] | None = None,
        data_path: str | Path = DATA_PATH,
        default_standard: str = "OISD-118",
    ):
        self._rows = rows
        self.data_path = Path(data_path)
        self.default_standard = default_standard.upper()

    def _records(self) -> list[dict[str, Any]]:
        rows = self._rows if self._rows is not None else load_json_records(self.data_path)
        return [row for row in rows if isinstance(row, dict)]

    def analyze(self, standard: str) -> dict[str, Any]:
        requested = standard.strip().upper()
        matched = [
            row
            for row in self._records()
            if str(row.get("standard") or self.default_standard).strip().upper() == requested
        ]
        if not matched:
            return self._no_data(requested)

        matrix = [self._matrix_row(row) for row in matched]
        compliant = sum(row["status"] == "COMPLIANT" for row in matrix)
        gaps = sum(row["status"] == "GAP" for row in matrix)
        critical = sum(row["status"] == "CRITICAL" for row in matrix)
        percentage = round(compliant / len(matrix) * 100, 2)
        actions = [
            {
                "rank": rank,
                "clause": row["clause"],
                "severity": row["severity"],
                "remediation": row["remediation"],
                "supporting_evidence_ids": [row["clause"]],
            }
            for rank, row in enumerate(
                sorted(
                    (item for item in matrix if item["status"] != "COMPLIANT"),
                    key=lambda item: (PRIORITY[item["status"]], item["clause"]),
                ),
                start=1,
            )
        ]
        confidence = round(mean(row["confidence"] for row in matrix), 2)
        return {
            "standard": requested,
            "requirements_checked": len(matrix),
            "matrix": matrix,
            "summary": {"compliant": compliant, "gaps": gaps, "critical": critical},
            "compliance_percentage": percentage,
            "corrective_actions": actions,
            "confidence": confidence,
            "assessment_type": "prototype evidence-gap assessment",
            "disclaimer": "This prototype evidence-gap assessment is not legal compliance certification.",
            "synthetic_data": True,
            "no_data": False,
        }

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        standard = state.get("standard") or self.default_standard
        return {**state, "final_response": self.analyze(str(standard))}

    @staticmethod
    def _matrix_row(row: dict[str, Any]) -> dict[str, Any]:
        status = str(row.get("status", "GAP")).strip().upper()
        if status not in STATUS_SEVERITY:
            status = "GAP"
        clause = str(row.get("clause") or row.get("requirement_id") or "UNSPECIFIED")
        requirement = str(row.get("requirement") or "Unspecified requirement")
        evidence = str(row.get("evidence") or row.get("evidence_source") or "No evidence supplied")
        present = sum(
            bool(row.get(field)) for field in ("clause", "requirement", "evidence", "status")
        )
        confidence = round(present / 4, 2)
        severity = str(row.get("severity") or STATUS_SEVERITY[status]).strip().upper()
        if row.get("remediation"):
            remediation = str(row["remediation"])
        elif status == "COMPLIANT":
            remediation = "Maintain the cited evidence and review it at the next inspection."
        elif status == "CRITICAL":
            remediation = f"Take immediate corrective action and verify evidence for: {requirement}."
        else:
            remediation = f"Close the evidence gap and verify: {requirement}."
        return {
            **row,
            "clause": clause,
            "requirement": requirement,
            "evidence": evidence,
            "evidence_source": evidence,
            "status": status,
            "severity": severity,
            "remediation": remediation,
            "confidence": confidence,
            "evidence_quality": "HIGH" if confidence >= 0.75 else "LIMITED",
            "supporting_evidence_ids": [clause],
        }

    @staticmethod
    def _no_data(standard: str) -> dict[str, Any]:
        return {
            "standard": standard,
            "requirements_checked": 0,
            "matrix": [],
            "summary": {"compliant": 0, "gaps": 0, "critical": 0},
            "compliance_percentage": 0.0,
            "corrective_actions": [],
            "confidence": 0.0,
            "assessment_type": "prototype evidence-gap assessment",
            "disclaimer": "No evidence is available; this is not legal compliance certification.",
            "synthetic_data": True,
            "no_data": True,
            "message": "No evidence available for the requested standard.",
        }
