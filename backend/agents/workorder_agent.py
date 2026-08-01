import json
import uuid
from datetime import datetime, timedelta, timezone

import google.generativeai as genai
from core.config import GEMINI_API_KEY

FALLBACK = {
    "recommended_actions": ["Inspect the identified failure mode", "Measure and record operating parameters", "Consult the OEM manual for tolerances"],
    "required_skills": ["Mechanical Engineer", "Instrumentation Technician"],
    "required_parts": ["Inspection consumables", "OEM-approved replacement parts"],
    "safety_precautions": ["Isolate equipment and apply LOTO", "Test for hazardous atmosphere", "Wear task-appropriate PPE"],
    "estimated_duration_hours": 6,
    "inspection_steps": ["Complete visual inspection", "Record dimensional and sensor checks", "Complete controlled functional test"],
}


class WorkOrderAgent:
    def __init__(self):
        self.model = None
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_work_order(self, equipment_id, risk_analysis, similar_incidents=None):
        score = risk_analysis.get("risk_score", 0)
        priority = "CRITICAL" if score >= 75 else "HIGH" if score >= 55 else "MEDIUM" if score >= 30 else "LOW"
        context = "\n".join(f'- {item["incident_id"]}: {item["root_cause"]}' for item in (similar_incidents or [])[:2]) or "No similar incidents found."
        content = FALLBACK
        if self.model:
            prompt = f'''Draft a maintenance work order as JSON with keys recommended_actions, required_skills, required_parts, safety_precautions, estimated_duration_hours, inspection_steps. Use only this evidence:\nEquipment: {equipment_id}\nRisk: {score}/100\nFailure mode: {risk_analysis.get("dominant_failure_mode")}\nRoot cause: {risk_analysis.get("dominant_root_cause")}\nSimilar incidents:\n{context}\nReturn JSON only.'''
            try:
                generated = json.loads(self.model.generate_content(prompt).text.strip().replace("```json", "").replace("```", ""))
                content = {key: generated.get(key, value) for key, value in FALLBACK.items()}
            except Exception:
                content = FALLBACK
        now = datetime.now(timezone.utc)
        due_hours = 24 if priority == "CRITICAL" else 72 if priority == "HIGH" else 168
        return {"work_order_id": f'WO-DRAFT-{now:%Y%m%d}-{str(uuid.uuid4())[:6].upper()}', "status": "DRAFT", "equipment_id": equipment_id, "priority": priority, "risk_score": score, "failure_mode": risk_analysis.get("dominant_failure_mode", "Unknown"), "root_cause_assessment": risk_analysis.get("dominant_root_cause", "Under investigation"), "created_at": now.isoformat(), "due_by": (now + timedelta(hours=due_hours)).isoformat(), "requires_approval": priority in {"CRITICAL", "HIGH"}, **content, "evidence_note": "Draft derived from synthetic historical evidence; engineer approval is required before execution."}

