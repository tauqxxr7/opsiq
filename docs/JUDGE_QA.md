# OPSIQ judge Q&A

## 1. What problem does OPSIQ solve?
It reduces manual cross-referencing across industrial work orders, inspections, incidents, manuals, and standards by offering grounded retrieval and reproducible specialist analysis.

## 2. Why is this not just ChatGPT over PDFs?
OPSIQ adds validated ingestion, hybrid retrieval, reranking, citations, deterministic specialist contracts, dataset identities, evidence IDs, no-data behavior, and cross-source graph analysis.

## 3. Why FastAPI?
FastAPI provides typed boundaries, OpenAPI documentation, Python-native integration with analytics and retrieval libraries, and an ASGI runtime suitable for containers.

## 4. Why ChromaDB?
It is a compact persistent vector store appropriate for this prototype. Its path is configurable and backed by Railway storage. A managed alternative would be benchmarked at enterprise scale.

## 5. Why hybrid BM25 plus dense retrieval?
Dense retrieval captures semantic similarity; BM25 preserves exact identifiers and technical terms. Their combination handles both natural-language paraphrases and clause/equipment codes.

## 6. Why cross-encoder reranking?
It jointly evaluates each query-passage pair after inexpensive candidate retrieval, improving ordering before limited context is sent for synthesis.

## 7. Why deterministic analytics?
The same evidence and methodology version produce the same specialist result. Component calculations remain inspectable and suitable for review.

## 8. How do you reduce hallucinations?
Retrieval precedes synthesis, candidates are reranked, citations are packaged, and absent evidence produces refusal. Gemini does not generate specialist scores. These controls reduce, not eliminate, model risk.

## 9. What happens when evidence is missing?
Unknown equipment or standards return `status: no_data`. The Copilot returns a no-evidence response and does not fabricate an answer.

## 10. How is maintenance risk calculated?
Six weighted components summarize dominant-failure recurrence, recency, ordinal severity, downtime burden, repeated root cause, and observed interval trend. The response exposes the breakdown.

## 11. Is the system predicting future failures?
No. It summarizes historical recurrence risk and does not predict a component or failure date.

## 12. Is compliance a legal certification?
No. It is a prototype evidence-gap assessment over six synthetic OISD-118 inspection records and requires qualified human review.

## 13. How are results traceable?
Responses carry supporting record IDs, dataset hashes, methodology versions, deterministic analysis IDs, component calculations, and limitations.

## 14. What data is used?
Fifty synthetic work orders, six synthetic inspection records, 11 recovered synthetic incident records, and user-uploaded PDF/DOCX documents.

## 15. Why synthetic data?
It enables a public, reproducible demonstration without exposing confidential plant, employee, safety, or operational records.

## 16. How would real plant data be onboarded?
Through approved connectors or controlled exports, schema validation, identity mapping, access controls, retention rules, quality checks, and domain-owner acceptance testing.

## 17. How would this scale to multiple plants?
Separate ingestion workers, object storage, PostgreSQL metadata, tenant-scoped indexes, queues, idempotent jobs, managed vector infrastructure, and stateless API scaling.

## 18. What are the current limitations?
Synthetic evidence, narrow compliance scope, no authentication or tenancy, small evaluation corpus, no live telemetry, and document-dependent retrieval quality.

## 19. What security controls exist today?
Secrets remain server-side, CORS is configurable, uploads are bounded and validated, duplicates are hashed, and containers exclude local secrets and runtime data.

## 20. What security controls are roadmap items?
SSO, RBAC, tenant isolation, encrypted storage, malware scanning, audit logs, retention controls, rate limits, private networking, and formal security testing.

## 21. How would authentication and tenancy work?
An identity provider would issue tenant-scoped claims; backend authorization would enforce plant and role boundaries, with separate metadata, object, and vector namespaces.

## 22. How does the failure-pattern graph help?
It connects equipment, failures, causes, and evidence records so reviewers can see recurrence and shared relationships that isolated chronological review may miss.

## 23. What is the main innovation?
Generative synthesis is evidence-gated while maintenance, compliance, and pattern analytics remain deterministic, inspectable, and reproducible.

## 24. How is this production-ready?
The prototype is containerized, environment-driven, CI-validated, persistently deployed, and publicly smoke-tested. Enterprise operational readiness still requires identity, tenancy, security, and plant-data validation.

## 25. What would you build next?
Controlled real-data evaluation, authentication and tenancy, retrieval benchmarks, asynchronous ingestion, human approval workflows, observability, and enterprise connectors.
