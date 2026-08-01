from core.config import GEMINI_API_KEY
from services.translation_service import TranslationService


class ExpertCopilotAgent:
    def __init__(self, retrieval=None):
        self.retrieval = retrieval
        self.translator = TranslationService()

    def run(self, state):
        original_query = state["query"]
        translation = self.translator.detect_and_translate_to_english(original_query)
        english_query = translation["translated"]
        language_code = translation["lang"]
        language_name = translation.get("lang_name", "English")
        chunks = (
            self.retrieval.hybrid_retrieve(english_query, top_k=20)
            if self.retrieval
            else state.get("retrieved_chunks", [])
        )
        metadata = {
            "detected_language": language_name,
            "detected_language_code": language_code,
            "query_translated": not translation["is_english"],
            "original_query": original_query,
        }

        if not chunks:
            answer = (
                "No relevant indexed evidence was found for this question. "
                "OPSIQ pre-loads the bundled synthetic work-order, inspection, and incident "
                "records when the knowledge index is empty. Upload industrial documents via "
                "the Document Library to enable domain-specific retrieval."
            )
            answer = self.translator.translate_response_to_language(answer, language_code)
            return {
                **state,
                "final_response": {
                    "answer": answer,
                    "citations": [],
                    "confidence": 0.0,
                    "follow_up_suggestions": [],
                    **metadata,
                },
                "error": "No grounded evidence",
            }

        citations = self._citations(chunks)
        confidence = self._confidence(chunks)
        if not GEMINI_API_KEY:
            return {
                **state,
                "final_response": {
                    "answer": "The required evidence was retrieved, but response synthesis is unavailable until GEMINI_API_KEY is configured.",
                    "citations": citations,
                    "confidence": confidence,
                    "follow_up_suggestions": [],
                    **metadata,
                },
                "error": "LLM not configured",
            }

        context = "\n\n".join(
            f'[{index + 1}] {chunk["doc_name"]} p.{chunk["page"]}: {chunk["text"]}'
            for index, chunk in enumerate(chunks)
        )
        prompt = (
            "You are OPSIQ Expert Copilot. Answer only from EVIDENCE. Cite claims as [1]. "
            f"If evidence is insufficient, say so.\nQUESTION: {english_query}\nEVIDENCE:\n{context}"
        )
        answer = self.translator.model.generate_content(prompt).text
        answer = self.translator.translate_response_to_language(answer, language_code)
        return {
            **state,
            "final_response": {
                "answer": answer,
                "citations": citations,
                "confidence": confidence,
                "follow_up_suggestions": [
                    "Show the supporting procedure",
                    "Check related equipment history",
                ],
                **metadata,
            },
        }

    @staticmethod
    def _citations(chunks):
        return [
            {
                "doc_name": chunk["doc_name"],
                "page": chunk["page"],
                "section": chunk["section"],
                "relevance_score": round(chunk["relevance_score"], 3),
                "excerpt": chunk["text"][:280],
            }
            for chunk in chunks[:3]
        ]

    @staticmethod
    def _confidence(chunks):
        return round(
            sum(chunk["relevance_score"] for chunk in chunks[:3])
            / min(3, len(chunks)),
            2,
        )