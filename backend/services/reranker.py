from sentence_transformers import CrossEncoder
class Reranker:
    def __init__(self):self.model=CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    def rank(self,query,chunks):
        scores=self.model.predict([[query,x["text"]] for x in chunks])
        return sorted(({**x,"score":float(s)} for x,s in zip(chunks,scores)),key=lambda x:x["score"],reverse=True)
