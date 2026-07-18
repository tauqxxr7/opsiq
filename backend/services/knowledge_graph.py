import networkx as nx
class KnowledgeGraph:
    def __init__(self):self.graph=nx.MultiDiGraph()
    def add_work_order(self,row):
        self.graph.add_edge(row["equipment_id"],row["failure_type"],relation="experienced",wo_id=row["wo_id"])
        self.graph.add_edge(row["failure_type"],row["root_cause"],relation="caused_by")
    def recurring_patterns(self,minimum=2):
        counts={}
        for source,target,data in self.graph.edges(data=True):
            if data.get("relation")=="experienced":counts[(source,target)]=counts.get((source,target),0)+1
        return [{"equipment_id":k[0],"failure_type":k[1],"occurrences":v} for k,v in counts.items() if v>=minimum]
