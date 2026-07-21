"""Offline, deterministic OPSIQ authenticity evaluation harness."""
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from agents.compliance_agent import ComplianceAgent
from agents.copilot_agent import ExpertCopilotAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.pattern_agent import PatternAgent


def evaluate():
    cases = json.loads((Path(__file__).with_name("cases.json")).read_text(encoding="utf-8-sig"))["cases"]
    results=[]
    for case in cases:
        kind=case["type"]
        if kind=="maintenance": output=MaintenanceAgent().analyze(case["input"]); passed=output["status"]==case["expected_status"]
        elif kind=="compliance":
            output=ComplianceAgent().analyze(case["input"]); passed=output.get("status")==case.get("expected_status") if "expected_status" in case else output["compliance_percentage"]==case["expected_percentage"]
        elif kind=="patterns": output=PatternAgent().analyze();passed=all(source in output["source_counts"] for source in case["expected_sources"])
        elif kind=="copilot_refusal": output=ExpertCopilotAgent().run({"query":"unsupported","retrieved_chunks":[]})["final_response"];passed=output["confidence"]==case["expected_confidence"] and output["citations"]==[] and "Insufficient" in output["answer"]
        else:
            chunks=[{"doc_name":"test.pdf","page":2,"section":"4.1","relevance_score":.8,"text":"Grounded evidence excerpt."}]
            output=ExpertCopilotAgent().run({"query":"test","retrieved_chunks":chunks})["final_response"]
            passed=bool(output["citations"]) and all(field in output["citations"][0] for field in case["required_fields"])
        results.append({"id":case["id"],"passed":passed})
    passed=sum(item["passed"] for item in results)
    return {"suite":"OPSIQ authenticity evaluation","version":"1.0.0","passed":passed,"total":len(results),"pass_rate":round(passed/len(results),3),"results":results}


if __name__=="__main__":
    report=evaluate();print(json.dumps(report,indent=2));raise SystemExit(0 if report["passed"]==report["total"] else 1)
