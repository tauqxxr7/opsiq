# OPSIQ submission deck

---

## Page 1 Ã¢â‚¬â€ OPSIQ

**Evidence-grounded industrial intelligence for maintenance, compliance, failure-pattern analysis, and engineering knowledge retrieval.**

Production-deployed prototype Ã‚Â· ET AI Hackathon 2.0 Ã‚Â· Problem Statement #8

![Dashboard](screenshots/dashboard-desktop.png)

---

## Page 2 Ã¢â‚¬â€ Industrial problem

Operational evidence is distributed across work orders, inspections, incidents, manuals, and standards. Manual search and cross-referencing slow engineering review and make knowledge transfer difficult.

OPSIQ provides one evidence layer without replacing source systems.

---

## Page 3 Ã¢â‚¬â€ Solution

- grounded document retrieval with citations;
- deterministic recurrence-risk analysis;
- prototype compliance evidence-gap assessment;
- cross-source failure-pattern investigation;
- evidence IDs, hashes, versions, and reproducible analysis identities.

---

## Page 4 Ã¢â‚¬â€ Architecture

React/Vite Ã¢â€ â€™ FastAPI Ã¢â€ â€™ LangGraph routing Ã¢â€ â€™ four specialist workflows.
ChromaDB and BM25 retrieve evidence; a cross-encoder reranks passages; optional Gemini synthesizes retrieved context. Deterministic agents calculate specialist results.

See [architecture](architecture.md).

---

## Page 5 Ã¢â‚¬â€ Evidence-first analytics

![Maintenance](screenshots/maintenance-desktop.png)

P-201 risk is derived from recurrence, recency, severity, downtime, repeated root cause, and interval trend. Compliance and pattern outputs also identify their supporting records. Missing evidence returns `no_data`.

---

## Page 6 Ã¢â‚¬â€ Live results

![Compliance](screenshots/compliance-desktop.png)

Verified public routes display live backend data for dashboard metrics, P-201 maintenance, OISD-118 evidence gaps, failure patterns, and document inventory.

---

## Page 7 Ã¢â‚¬â€ Limitations and roadmap

**Current:** synthetic evidence, narrow OISD-118 scope, environment-gated single-tenant authentication, SQLite operational persistence, small regression evaluation, and no live telemetry.

**Next:** controlled plant-data validation, access control, tenant isolation, retrieval evaluation, asynchronous ingestion, human approval workflows, security hardening, and enterprise connectors.

---

## Page 8 Ã¢â‚¬â€ Explore OPSIQ

- Application: https://opsiq-one.vercel.app
- API documentation: https://opsiq-production-b20c.up.railway.app/docs
- Repository: https://github.com/tauqxxr7/opsiq
- Author: Tauqeer Bharde Ã¢â‚¬â€ https://github.com/tauqxxr7

Released under the MIT License.
