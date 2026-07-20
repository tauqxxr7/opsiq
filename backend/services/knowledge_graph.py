from collections import Counter, defaultdict
from typing import Any


class KnowledgeGraph:
    """Evidence-backed graph serialized without a database or model dependency."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: dict[tuple[str, str, str], dict[str, Any]] = {}
        self._evidence: dict[tuple[str, str, str], set[str]] = defaultdict(set)

    def add_record(self, record: dict[str, Any]) -> None:
        equipment = str(record.get("equipment_id") or "").strip()
        failure = str(record.get("failure_type") or "").strip()
        cause = str(record.get("root_cause") or "").strip()
        evidence_id = str(record.get("record_id") or "").strip()
        source = str(record.get("source") or "unknown")
        if not equipment:
            return
        equipment_node = f"equipment:{equipment}"
        self.nodes[equipment_node] = {"label": equipment, "node_type": "equipment"}
        if failure:
            failure_node = f"failure:{failure}"
            self.nodes[failure_node] = {"label": failure, "node_type": "failure_mode"}
            self._add_edge(equipment_node, failure_node, "experienced", evidence_id, source)
        if cause:
            cause_node = f"root:{cause}"
            self.nodes[cause_node] = {"label": cause, "node_type": "root_cause"}
            self._add_edge(equipment_node, cause_node, "attributed_to", evidence_id, source)
            if failure:
                self._add_edge(f"failure:{failure}", cause_node, "caused_by", evidence_id, source)

    def add_work_order(self, row: dict[str, Any]) -> None:
        self.add_record({**row, "record_id": row.get("wo_id"), "source": "work_order"})

    def _add_edge(self, source: str, target: str, relation: str, evidence_id: str, origin: str) -> None:
        ordered = tuple(sorted((source, target)))
        key = ordered + (relation,)
        if evidence_id:
            self._evidence[key].add(evidence_id)
        origins = set(self.edges.get(key, {}).get("sources", []))
        origins.add(origin)
        self.edges[key] = {"source": ordered[0], "target": ordered[1], "relation": relation,
                           "weight": len(self._evidence[key]), "evidence_ids": sorted(self._evidence[key]),
                           "sources": sorted(origins)}

    def recurring_patterns(self, minimum: int = 2) -> list[dict[str, Any]]:
        patterns = []
        for edge in self.edges.values():
            source, target = edge["source"], edge["target"]
            source_type, target_type = self.nodes[source]["node_type"], self.nodes[target]["node_type"]
            if {source_type, target_type} != {"equipment", "failure_mode"} or edge["weight"] < minimum:
                continue
            equipment_node = source if source_type == "equipment" else target
            failure_node = target if target_type == "failure_mode" else source
            patterns.append({"equipment_id": self.nodes[equipment_node]["label"],
                             "failure_type": self.nodes[failure_node]["label"],
                             "occurrences": edge["weight"],
                             "supporting_evidence_ids": edge["evidence_ids"]})
        return sorted(patterns, key=lambda row: (-row["occurrences"], row["equipment_id"], row["failure_type"]))

    def serialize(self) -> dict[str, Any]:
        degrees = Counter()
        adjacency: dict[str, set[str]] = defaultdict(set)
        for edge in self.edges.values():
            degrees[edge["source"]] += edge["weight"]
            degrees[edge["target"]] += edge["weight"]
            adjacency[edge["source"]].add(edge["target"])
            adjacency[edge["target"]].add(edge["source"])
        components, remaining = 0, set(self.nodes)
        while remaining:
            components += 1
            stack = [remaining.pop()]
            while stack:
                for neighbor in adjacency[stack.pop()] & remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
        nodes = [{"id": node_id, **data, "weighted_degree": degrees[node_id]} for node_id, data in self.nodes.items()]
        return {"nodes": sorted(nodes, key=lambda node: node["id"]),
                "edges": sorted(self.edges.values(), key=lambda edge: (edge["source"], edge["target"], edge["relation"])),
                "metrics": {"node_count": len(self.nodes), "edge_count": len(self.edges),
                            "connected_components": components}}

