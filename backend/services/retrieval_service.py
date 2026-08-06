import re
import threading

from core.config import CHROMA_DB_PATH

_instance_lock = threading.Lock()


class RetrievalService:
    _instances = {}

    def __new__(cls):
        instance_key = str(CHROMA_DB_PATH)
        if instance_key not in cls._instances:
            with _instance_lock:
                if instance_key not in cls._instances:
                    instance = super().__new__(cls)
                    instance._configured = False
                    instance._model_lock = threading.Lock()
                    cls._instances[instance_key] = instance
        return cls._instances[instance_key]

    def __init__(self):
        if self._configured:
            return
        with _instance_lock:
            if self._configured:
                return
            self.collection = None
            self.encoder = None
            self._reranker = None
            self.bm25 = None
            self.ids = []
            self.documents = []
            self.metadatas = []
            self._np = None
            self._bm25_class = None
            self._configured = True

    @property
    def initialized(self):
        return self.collection is not None

    @property
    def reranker(self):
        if self._reranker is None:
            from sentence_transformers import CrossEncoder

            self._reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        return self._reranker

    def initialize(self):
        """Load the vector store and ML models exactly once for this persistence path."""
        self._ensure_initialized()
        return self

    def _ensure_initialized(self):
        if self.initialized:
            return
        with self._model_lock:
            if self.initialized:
                return
            import chromadb
            import numpy as np
            from rank_bm25 import BM25Okapi
            from sentence_transformers import SentenceTransformer

            self._np = np
            self._bm25_class = BM25Okapi
            collection = chromadb.PersistentClient(path=CHROMA_DB_PATH).get_or_create_collection(
                "opsiq_documents", metadata={"hnsw:space": "cosine"}
            )
            encoder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
            self.collection = collection
            self.encoder = encoder
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
