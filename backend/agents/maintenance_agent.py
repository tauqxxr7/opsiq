import json
from pathlib import Path
class MaintenanceAgent:
    def run(self,state):
        rows=json.loads((Path(__file__).parents[1]/"data/synthetic/work_orders.json").read_text())
        equipment=state.get("equipment_id") or "P-201"; history=[x for x in rows if x["equipment_id"]==equipment]
        return {**state,"final_response":{"equipment_id":equipment,"risk_level":"CRITICAL" if len(history)>=4 else "MONITOR","predicted_component":"Mechanical seal / bearing assembly","failure_window":"3–5 days" if len(history)>=4 else "No imminent signature","history":history,"confidence":0.88}}
