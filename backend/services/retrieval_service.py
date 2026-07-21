import re

from core.config import CHROMA_DB_PATH


class RetrievalService:
    def __init__(self):
        self.collection = None
        self.encoder = None
        self.reranker = None
        self.bm25 = None
        self.ids = []
        self.documents = []
        self.metadatas = []
        self._np = None
        self._bm25_class = None

    @property
    def initialized(self):
        return self.collection is not None

    def _ensure_initialized(self):
        if self.initialized:
            return
        import chromadb
        import numpy as np
        from rank_bm25 import BM25Okapi
        from sentence_transformers import CrossEncoder, SentenceTransformer

        self._np = np
        self._bm25_class = BM25Okapi
        self.collection = chromadb.PersistentClient(path=CHROMA_DB_PATH).get_or_create_collection(
            "opsiq_documents", metadata={"hnsw:space": "cosine"}
        )
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        self._refresh()

    def _tokens(self, text):
        return re.findall(r"[a-z0-9-]+", text.lower())

    def _refresh(self):
        data = self.collection.get(include=["documents", "metadatas"])
        self.ids = data["ids"]
        self.documents = data["documents"]
        self.metadatas = data["metadatas"]
        self.bm25 = (
            self._bm25_class([self._tokens(document) for document in self.documents])
            if self.documents else None
        )

    def add_documents(self, chunks):
        if not chunks:
            return
        self._ensure_initialized()
        texts = [chunk["text"] for chunk in chunks]
        self.collection.upsert(
            ids=[chunk["chunk_id"] for chunk in chunks],
            documents=texts,
            embeddings=self.encoder.encode(texts, normalize_embeddings=True).tolist(),
            metadatas=[
                {key: chunk[key] for key in ("doc_name", "page", "section", "doc_type")}
                for chunk in chunks
            ],
        )
        self._refresh()

    def hybrid_retrieve(self, query, top_k=20):
        self._ensure_initialized()
        if not self.documents:
            return []
        dense = self.collection.query(
            query_embeddings=self.encoder.encode([query], normalize_embeddings=True).tolist(),
            n_results=min(top_k, len(self.documents)),
        )
        fused = {}
        for rank, key in enumerate(dense["ids"][0]):
            fused[key] = fused.get(key, 0) + 1 / (61 + rank)
        for rank, index in enumerate(
            self._np.argsort(self.bm25.get_scores(self._tokens(query)))[::-1][:top_k]
        ):
            key = self.ids[index]
            fused[key] = fused.get(key, 0) + 1 / (61 + rank)
        lookup = {key: index for index, key in enumerate(self.ids)}
        items = [
            {"id": key, "text": self.documents[lookup[key]], **self.metadatas[lookup[key]]}
            for key, _ in sorted(fused.items(), key=lambda item: item[1], reverse=True)[:top_k]
        ]
        scores = self.reranker.predict([[query, item["text"]] for item in items])
        for item, score in zip(items, scores):
            item["relevance_score"] = float(1 / (1 + self._np.exp(-score)))
        return sorted(items, key=lambda item: item["relevance_score"], reverse=True)[:5]

    def count(self):
        if self.collection is not None:
            return self.collection.count()
        import chromadb

        collection = chromadb.PersistentClient(path=CHROMA_DB_PATH).get_or_create_collection(
            "opsiq_documents", metadata={"hnsw:space": "cosine"}
        )
        return collection.count()
