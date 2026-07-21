from core.config import GEMINI_API_KEY
class ExpertCopilotAgent:
    def __init__(self,retrieval=None):self.retrieval=retrieval
    def run(self,state):
        chunks=(self.retrieval.hybrid_retrieve(state["query"]) if self.retrieval else state.get("retrieved_chunks",[]))
        if not chunks:return {**state,"final_response":{"answer":"Insufficient documentation found to answer safely.","citations":[],"confidence":0.0,"follow_up_suggestions":[]},"error":"No grounded evidence"}
        context="\n\n".join(f'[{i+1}] {x["doc_name"]} p.{x["page"]}: {x["text"]}' for i,x in enumerate(chunks))
        if not GEMINI_API_KEY:return {**state,"final_response":{"answer":"The required evidence was retrieved, but response synthesis is unavailable until GEMINI_API_KEY is configured.","citations":self._citations(chunks),"confidence":self._confidence(chunks),"follow_up_suggestions":[]},"error":"LLM not configured"}
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        prompt=f"""You are OPSIQ Expert Copilot. Answer only from EVIDENCE. Cite claims as [1]. If evidence is insufficient, say so.\nQUESTION: {state['query']}\nEVIDENCE:\n{context}"""
        answer=genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt).text
        return {**state,"final_response":{"answer":answer,"citations":self._citations(chunks),"confidence":self._confidence(chunks),"follow_up_suggestions":["Show the supporting procedure","Check related equipment history"]}}
    def _citations(self,chunks):return [{"doc_name":x["doc_name"],"page":x["page"],"section":x["section"],"relevance_score":round(x["relevance_score"],3),"excerpt":x["text"][:280]} for x in chunks[:3]]
    def _confidence(self,chunks):return round(sum(x["relevance_score"] for x in chunks[:3])/min(3,len(chunks)),2)

