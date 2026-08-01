import json
import time
from pathlib import Path

from fastapi import APIRouter, Request

router = APIRouter()
BENCHMARK_PATH = Path(__file__).parents[1] / "data" / "evaluation" / "benchmark.json"


@router.get("/run")
async def run_benchmark(request: Request):
    """Run the predefined retrieval-quality benchmark against the active index."""
    if not BENCHMARK_PATH.exists():
        return {"error": "Benchmark file not found"}

    benchmark = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    retrieval = request.app.state.retrieval_service
    results = []

    for item in benchmark["queries"]:
        started = time.perf_counter()
        candidates = retrieval.hybrid_retrieve(item["query"], top_k=5)
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        confidence = round(
            sum(candidate.get("relevance_score", 0) for candidate in candidates)
            / len(candidates),
            3,
        ) if candidates else 0.0
        top_text = candidates[0]["text"].lower() if candidates else ""
        keyword_hits = sum(
            keyword.lower() in top_text for keyword in item["expected_keywords"]
        )
        coverage = round(keyword_hits / len(item["expected_keywords"]) * 100)
        top_candidate = candidates[0] if candidates else {}
        results.append({
            "query_id": item["id"],
            "query": item["query"],
            "category": item["category"],
            "confidence": confidence,
            "keyword_coverage_pct": coverage,
            "results_returned": len(candidates),
            "response_time_ms": elapsed_ms,
            "top_source": top_candidate.get("doc_name", "none"),
            "top_doc_type": top_candidate.get("doc_type", "none"),
            "expected_doc_type_match": top_candidate.get("doc_type") == item["expected_doc_type"],
        })

    count = len(results)
    return {
        "benchmark_version": benchmark["version"],
        "queries_evaluated": count,
        "aggregate": {
            "mean_retrieval_confidence": round(sum(row["confidence"] for row in results) / count, 2) if count else 0,
            "mean_response_time_ms": round(sum(row["response_time_ms"] for row in results) / count) if count else 0,
            "mean_keyword_coverage_pct": round(sum(row["keyword_coverage_pct"] for row in results) / count) if count else 0,
            "expected_doc_type_match_pct": round(sum(row["expected_doc_type_match"] for row in results) / count * 100) if count else 0,
        },
        "results": results,
    }
