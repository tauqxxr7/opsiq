from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from services.evidence_loader import load_json_records
from services.knowledge_graph import KnowledgeGraph

DATA_DIR = Path(__file__).parents[1] / "data/synthetic"


class PatternAgent:
    def __init__(self, work_orders=None, incident_history=None,
                 work_order_path=DATA_DIR / "work_orders.json",
                 incident_path=DATA_DIR / "incident_history.json") -> None:
        self._work_orders = work_orders
        self._incidents = incident_history
        self.work_order_path = Path(work_order_path)
        self.incident_path = Path(incident_path)

    def analyze(self) -> dict[str, Any]:
        records = self._records()
        graph = KnowledgeGraph()
        for record in records:
            graph.add_record(record)
        if not records:
            return self._empty(graph)
        combinations, roots, precursors, failures = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
        for record in records:
            equipment, failure = record["equipment_id"], record["failure_type"]
            if equipment and failure:
                combinations[(equipment, failure)].append(record)
            if record["root_cause"]:
                roots[record["root_cause"]].append(record)
            if failure:
                failures[failure].append(record)
            for precursor in record["precursors"]:
                precursors[precursor].append(record)
        patterns = [self._pattern(eq, failure, rows) for (eq, failure), rows in combinations.items() if len(rows) >= 2]
        root_patterns = [self._aggregate("root_cause", cause, rows) for cause, rows in roots.items()
                         if len({row["equipment_id"] for row in rows if row["equipment_id"]}) >= 2]
        downtime_clusters = [{**self._aggregate("failure_type", failure, rows),
                              "cumulative_downtime_hours": round(sum(row["downtime_hours"] for row in rows), 1)}
                             for failure, rows in failures.items()
                             if sum(row["downtime_hours"] for row in rows) >= 20]
        precursor_patterns = [self._aggregate("precursor", value, rows)
                              for value, rows in precursors.items() if len(rows) >= 2]
        source_counts = Counter(record["source"] for record in records)
        completeness = sum(bool(r["equipment_id"] and r["failure_type"] and r["record_id"]) for r in records) / len(records)
        return {
            "patterns": sorted(patterns, key=lambda row: (-row["occurrences"], row["equipment_id"], row["failure_type"])),
            "recurring_root_causes": sorted(root_patterns, key=lambda row: (-row["occurrences"], row["value"])),
            "high_downtime_clusters": sorted(downtime_clusters, key=lambda row: -row["cumulative_downtime_hours"]),
            "repeated_precursors": sorted(precursor_patterns, key=lambda row: (-row["occurrences"], row["value"])),
            "knowledge_graph": graph.serialize(), "records_analyzed": len(records),
            "source_counts": dict(sorted(source_counts.items())),
            "confidence": round(min(1.0, .2 + .5 * min(len(records) / 30, 1) + .3 * completeness), 2),
            "analysis_type": "deterministic cross-source pattern aggregation",
            "synthetic_data": True, "no_data": False}

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        return {**state, "final_response": self.analyze()}

    def _records(self) -> list[dict[str, Any]]:
        work = self._work_orders if self._work_orders is not None else load_json_records(self.work_order_path)
        incidents = self._incidents if self._incidents is not None else load_json_records(self.incident_path)
        rows = [self._normalize(row, "work_order") for row in work]
        rows += [self._normalize(row, "incident_history") for row in incidents]
        return [row for row in rows if row["record_id"] or row["equipment_id"]]

    @staticmethod
    def _normalize(row: dict[str, Any], source: str) -> dict[str, Any]:
        symptoms = row.get("symptoms") or row.get("operating_condition") or row.get("condition") or ""
        values = symptoms if isinstance(symptoms, list) else str(symptoms).replace(",", ";").split(";")
        try:
            downtime = max(0.0, float(row.get("downtime_hours") or 0))
        except (TypeError, ValueError):
            downtime = 0.0
        return {"record_id": str(row.get("wo_id") or row.get("incident_id") or row.get("id") or ""),
                "equipment_id": str(row.get("equipment_id") or "").strip(),
                "failure_type": str(row.get("failure_type") or row.get("failure_mode") or "").strip(),
                "root_cause": str(row.get("root_cause") or "").strip(),
                "date": str(row.get("date") or row.get("incident_date") or ""),
                "downtime_hours": downtime,
                "precursors": sorted({str(value).strip() for value in values if str(value).strip()}),
                "source": source}

    @staticmethod
    def _evidence(rows):
        return sorted({row["record_id"] for row in rows if row["record_id"]})

    def _pattern(self, equipment, failure, rows):
        dates = sorted(row["date"] for row in rows if row["date"])
        return {"equipment_id": equipment, "failure_type": failure, "occurrences": len(rows),
                "risk": "CRITICAL" if len(rows) >= 4 else "WATCH",
                "first_seen": dates[0] if dates else None, "last_seen": dates[-1] if dates else None,
                "cumulative_downtime_hours": round(sum(row["downtime_hours"] for row in rows), 1),
                "sources": sorted({row["source"] for row in rows}),
                "supporting_evidence_ids": self._evidence(rows)}

    def _aggregate(self, dimension, value, rows):
        return {"dimension": dimension, "value": value, "occurrences": len(rows),
                "equipment_ids": sorted({row["equipment_id"] for row in rows if row["equipment_id"]}),
                "sources": sorted({row["source"] for row in rows}),
                "supporting_evidence_ids": self._evidence(rows)}

    @staticmethod
    def _empty(graph):
        return {"patterns": [], "recurring_root_causes": [], "high_downtime_clusters": [],
                "repeated_precursors": [], "knowledge_graph": graph.serialize(), "records_analyzed": 0,
                "source_counts": {}, "confidence": 0.0,
                "analysis_type": "deterministic cross-source pattern aggregation", "synthetic_data": True,
                "no_data": True, "message": "No evidence is available for pattern analysis."}
