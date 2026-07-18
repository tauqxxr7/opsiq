import re, chromadb, numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from core.config import CHROMA_DB_PATH
class RetrievalService:
    def __init__(self):
        self.collection=chromadb.PersistentClient(path=CHROMA_DB_PATH).get_or_create_collection("opsiq_documents",metadata={"hnsw:space":"cosine"})
        self.encoder=SentenceTransformer("all-MiniLM-L6-v2"); self.reranker=CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2"); self._refresh()
    def _tokens(self,text):return re.findall(r"[a-z0-9-]+",text.lower())
    def _refresh(self):
        data=self.collection.get(include=["documents","metadatas"]); self.ids=data["ids"]; self.documents=data["documents"]; self.metadatas=data["metadatas"]
        self.bm25=BM25Okapi([self._tokens(x) for x in self.documents]) if self.documents else None
    def add_documents(self,chunks):
        if not chunks:return
        texts=[x["text"] for x in chunks]
        self.collection.upsert(ids=[x["chunk_id"] for x in chunks],documents=texts,embeddings=self.encoder.encode(texts,normalize_embeddings=True).tolist(),metadatas=[{k:x[k] for k in ("doc_name","page","section","doc_type")} for x in chunks]); self._refresh()
    def hybrid_retrieve(self,query,top_k=20):
        if not self.documents:return []
        dense=self.collection.query(query_embeddings=self.encoder.encode([query],normalize_embeddings=True).tolist(),n_results=min(top_k,len(self.documents)))
        fused={}
        for rank,key in enumerate(dense["ids"][0]):fused[key]=fused.get(key,0)+1/(61+rank)
        for rank,index in enumerate(np.argsort(self.bm25.get_scores(self._tokens(query)))[::-1][:top_k]):key=self.ids[index];fused[key]=fused.get(key,0)+1/(61+rank)
        lookup={key:i for i,key in enumerate(self.ids)}
        items=[{"id":key,"text":self.documents[lookup[key]],**self.metadatas[lookup[key]]} for key,_ in sorted(fused.items(),key=lambda x:x[1],reverse=True)[:top_k]]
        scores=self.reranker.predict([[query,x["text"]] for x in items])
        for item,score in zip(items,scores):item["relevance_score"]=float(1/(1+np.exp(-score)))
        return sorted(items,key=lambda x:x["relevance_score"],reverse=True)[:5]
