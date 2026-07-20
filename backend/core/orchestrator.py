from core.state import OpsIQState


def route_query(state):
    query = state["query"].lower()
    groups = {
        "maintenance": ["pump", "valve", "failure", "maintenance", "vibration", "bearing", "seal"],
        "compliance": ["oisd", "factory act", "dgms", "peso", "compliance", "audit", "standard"],
        "pattern": ["pattern", "recurring", "history", "trend", "systemic", "repeated"],
    }
    query_type = next(
        (kind for kind, words in groups.items() if any(word in query for word in words)),
        "copilot",
    )
    return {**state, "query_type": state.get("query_type") or query_type}


def _compile_graph(retrieval=None):
    from langgraph.graph import END, StateGraph
    from agents.compliance_agent import ComplianceAgent
    from agents.copilot_agent import ExpertCopilotAgent
    from agents.maintenance_agent import MaintenanceAgent
    from agents.pattern_agent import PatternAgent

    graph = StateGraph(OpsIQState)
    graph.add_node("router", route_query)
    for name, agent in [
        ("copilot", ExpertCopilotAgent(retrieval)),
        ("maintenance", MaintenanceAgent()),
        ("compliance", ComplianceAgent()),
        ("pattern", PatternAgent()),
    ]:
        graph.add_node(name, agent.run)
        graph.add_edge(name, END)
    graph.set_entry_point("router")
    graph.add_conditional_edges(
        "router",
        lambda state: state["query_type"],
        {name: name for name in ("copilot", "maintenance", "compliance", "pattern")},
    )
    return graph.compile()


class LazyGraph:
    def __init__(self, retrieval=None):
        self.retrieval = retrieval
        self._graph = None

    @property
    def initialized(self):
        return self._graph is not None

    async def ainvoke(self, state):
        if self._graph is None:
            self._graph = _compile_graph(self.retrieval)
        return await self._graph.ainvoke(state)


def build_graph(retrieval=None):
    return LazyGraph(retrieval)
