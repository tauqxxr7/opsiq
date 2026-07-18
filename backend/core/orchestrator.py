from langgraph.graph import StateGraph,END
from agents.copilot_agent import ExpertCopilotAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.compliance_agent import ComplianceAgent
from agents.pattern_agent import PatternAgent
from core.state import OpsIQState
def route_query(state):
    query=state["query"].lower()
    groups={"maintenance":["pump","valve","failure","maintenance","vibration","bearing","seal"],"compliance":["oisd","factory act","dgms","peso","compliance","audit","standard"],"pattern":["pattern","recurring","history","trend","systemic","repeated"]}
    query_type=next((kind for kind,words in groups.items() if any(word in query for word in words)),"copilot")
    return {**state,"query_type":state.get("query_type") or query_type}
def build_graph(retrieval=None):
    graph=StateGraph(OpsIQState); graph.add_node("router",route_query)
    for name,agent in [("copilot",ExpertCopilotAgent(retrieval)),("maintenance",MaintenanceAgent()),("compliance",ComplianceAgent()),("pattern",PatternAgent())]:
        graph.add_node(name,agent.run);graph.add_edge(name,END)
    graph.set_entry_point("router");graph.add_conditional_edges("router",lambda s:s["query_type"],{x:x for x in ("copilot","maintenance","compliance","pattern")})
    return graph.compile()
