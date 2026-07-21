from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from core.evidence import IncidentRecord, WorkOrderRecord, dataset_sha256, deterministic_analysis_id, load_records
from core.methodology import PATTERN_METHODOLOGY_VERSION
from services.knowledge_graph import KnowledgeGraph

DATA_DIR = Path(__file__).parents[1] / "data/synthetic"


class PatternAgent:
    def __init__(self, work_orders=None, incidents=None, work_path=DATA_DIR/"work_orders.json", incident_path=DATA_DIR/"incident_history.json"):
        self._work_orders, self._incidents = work_orders, incidents
        self.work_path, self.incident_path = Path(work_path), Path(incident_path)

    def _records(self):
        work = self._work_orders if self._work_orders is not None else load_records(self.work_path, WorkOrderRecord)
        incidents = self._incidents if self._incidents is not None else load_records(self.incident_path, IncidentRecord)
        normalized = []
        for raw in work:
            row = raw.model_dump() if hasattr(raw, "model_dump") else raw
            symptoms = str(row.get("symptoms", "")).replace(",", ";").split(";")
            normalized.append({"record_id": row["work_order_id"], "equipment_id": row["equipment_id"], "failure_type": row["failure_type"], "root_cause": row["root_cause"], "date": row["date"], "downtime_hours": float(row["downtime_hours"]), "precursors": sorted({x.strip() for x in symptoms if x.strip()}), "source": "work_order"})
        for raw in incidents:
            row = raw.model_dump() if hasattr(raw, "model_dump") else raw
            normalized.append({"record_id": row["incident_id"], "equipment_id": row["equipment_id"], "failure_type": row["failure_mode"], "root_cause": row["root_cause"], "date": row["date"], "downtime_hours": 0.0, "precursors": [row["condition"]] if row.get("condition") else [], "source": "incident_history"})
        return normalized

    def analyze(self):
        rows = self._records()
        graph = KnowledgeGraph()
        for row in rows: graph.add_record(row)
        dataset_hash = dataset_sha256(self.work_path, self.incident_path) if self._work_orders is None and self._incidents is None else deterministic_analysis_id("fixture", {"rows": rows}, "fixture", "v1")
        metadata = {"analysis_id": deterministic_analysis_id("patterns", {}, dataset_hash, PATTERN_METHODOLOGY_VERSION), "dataset_hash": dataset_hash, "methodology_version": PATTERN_METHODOLOGY_VERSION, "generated_at": datetime.now(timezone.utc).isoformat(), "synthetic_data": True}
        if not rows:
            return {"status": "no_data", "message": "No evidence is available for pattern analysis.", "patterns": [], "evidence": [], "limitations": ["No source records were loaded."], "metadata": metadata}
        combinations, roots, failures, precursors = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
        for row in rows:
            combinations[(row["equipment_id"], row["failure_type"])].append(row)
            roots[row["root_cause"]].append(row); failures[row["failure_type"]].append(row)
            for value in row["precursors"]: precursors[value].append(row)
        patterns = [self._pattern(eq, failure, items) for (eq, failure), items in combinations.items() if len(items)>=2]
        root_patterns = [self._aggregate("root_cause", value, items) for value, items in roots.items() if value and len({x["equipment_id"] for x in items})>=2]
        downtime = [{**self._aggregate("failure_type", value, items), "cumulative_downtime_hours": round(sum(x["downtime_hours"] for x in items),1)} for value, items in failures.items() if sum(x["downtime_hours"] for x in items)>=20]
        precursor_patterns = [self._aggregate("precursor", value, items) for value, items in precursors.items() if len(items)>=2]
        source_counts = Counter(row["source"] for row in rows)
        evidence_ids = sorted({row["record_id"] for row in rows})
        return {"status": "ok", "patterns": sorted(patterns,key=lambda x:(-x["occurrences"],x["equipment_id"],x["failure_type"])), "recurring_root_causes": sorted(root_patterns,key=lambda x:(-x["occurrences"],x["value"])), "high_downtime_clusters": sorted(downtime,key=lambda x:-x["cumulative_downtime_hours"]), "repeated_precursors": sorted(precursor_patterns,key=lambda x:(-x["occurrences"],x["value"])), "knowledge_graph": graph.serialize(), "records_analyzed": len(rows), "source_counts": dict(sorted(source_counts.items())), "evidence": [{"record_id": value} for value in evidence_ids], "supporting_evidence_ids": evidence_ids, "confidence": round(.4*min(len(rows)/30,1)+.3*int(len(source_counts)>=2)+.3,2), "methodology": {"name": "deterministic cross-source pattern aggregation", "recurring_threshold": 2, "high_downtime_threshold_hours": 20}, "limitations": ["Associations are historical correlations and do not establish causality.", "Incident-history downtime is unavailable and contributes zero hours."], "metadata": metadata}

    @staticmethod
    def _ids(rows): return sorted({row["record_id"] for row in rows})
    def _pattern(self, equipment, failure, rows):
        dates=sorted(row["date"] for row in rows if row["date"])
        return {"equipment_id": equipment, "failure_type": failure, "occurrences": len(rows), "risk": "CRITICAL" if len(rows)>=4 else "WATCH", "first_seen": dates[0] if dates else None, "last_seen": dates[-1] if dates else None, "cumulative_downtime_hours": round(sum(row["downtime_hours"] for row in rows),1), "sources": sorted({row["source"] for row in rows}), "supporting_evidence_ids": self._ids(rows)}
    def _aggregate(self, dimension, value, rows):
        return {"dimension": dimension, "value": value, "occurrences": len(rows), "equipment_ids": sorted({row["equipment_id"] for row in rows}), "sources": sorted({row["source"] for row in rows}), "supporting_evidence_ids": self._ids(rows)}
    def run(self, state): return {**state, "final_response": self.analyze()}
