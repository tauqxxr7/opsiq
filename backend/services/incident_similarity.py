from pathlib import Path

from core.evidence import IncidentRecord, load_records

DATA_PATH = Path(__file__).parents[1] / "data/synthetic/incident_history.json"


class IncidentSimilarityEngine:
    def __init__(self, data_path=DATA_PATH):
        self.data_path = Path(data_path)

    def find_similar(self, query_description, equipment_id=None, top_k=3):
        query_words = set(query_description.lower().split())
        scored = []
        for record in load_records(self.data_path, IncidentRecord):
            incident = record.model_dump()
            combined = f'{incident.get("condition", "")} {incident["failure_mode"]} {incident["root_cause"]}'.lower()
            words = set(combined.split())
            text_score = len(query_words & words) / len(query_words | words) if query_words | words else 0
            score = min(1, text_score + (.3 if equipment_id and incident["equipment_id"] == equipment_id.upper() else 0))
            if score > .05:
                scored.append({**incident, "similarity_score": round(score, 3)})
        return sorted(scored, key=lambda item: item["similarity_score"], reverse=True)[:max(1, min(top_k, 10))]
