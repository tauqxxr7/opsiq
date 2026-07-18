from typing import Any, Dict, List, Optional, TypedDict
class Citation(TypedDict):
    doc_name: str; page: int; section: str; relevance_score: float; excerpt: str
class OpsIQState(TypedDict, total=False):
    query: str; query_type: str; equipment_id: Optional[str]; standard: Optional[str]
    retrieved_chunks: List[Dict[str, Any]]; agent_outputs: Dict[str, Any]
    final_response: Dict[str, Any]; citations: List[Citation]; confidence_score: float; error: Optional[str]
