import json
from pathlib import Path
from collections import Counter
class PatternAgent:
    def run(self,state):
        rows=json.loads((Path(__file__).parents[1]/"data/synthetic/work_orders.json").read_text())
        counts=Counter((x["equipment_id"],x["failure_type"]) for x in rows)
        patterns=[{"equipment_id":a,"failure_type":b,"occurrences":n,"risk":"CRITICAL" if n>=4 else "WATCH"} for (a,b),n in counts.items() if n>=2]
        return {**state,"final_response":{"patterns":patterns,"records_analyzed":len(rows),"confidence":0.93}}
