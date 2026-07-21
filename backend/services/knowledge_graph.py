import networkx as nx


class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_record(self, record):
        evidence = record["record_id"]
        equipment = f'equipment:{record["equipment_id"]}'
        failure = f'failure:{record["failure_type"]}'
        self.graph.add_node(equipment, type="equipment", label=record["equipment_id"])
        self.graph.add_node(failure, type="failure_mode", label=record["failure_type"])
        self.graph.add_edge(equipment, failure, relation="experienced", evidence_id=evidence, source=record["source"])
        if record["root_cause"]:
            cause = f'cause:{record["root_cause"]}'
            self.graph.add_node(cause, type="root_cause", label=record["root_cause"])
            self.graph.add_edge(failure, cause, relation="caused_by", evidence_id=evidence, source=record["source"])
        for precursor in record["precursors"]:
            symptom = f"precursor:{precursor}"
            self.graph.add_node(symptom, type="precursor", label=precursor)
            self.graph.add_edge(symptom, failure, relation="precedes", evidence_id=evidence, source=record["source"])

    def serialize(self):
        return {"directed": True, "multigraph": True, "node_count": self.graph.number_of_nodes(), "edge_count": self.graph.number_of_edges(), "nodes": [{"id": node, **data} for node, data in self.graph.nodes(data=True)], "edges": [{"source": source, "target": target, **data} for source, target, data in self.graph.edges(data=True)]}
