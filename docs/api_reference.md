
# API Reference

Base URL: `http://localhost:8000`

- `GET /health` — liveness status.
- `POST /api/documents/upload` — multipart `file` field; PDF/DOCX only. Returns pipeline stages and indexed chunk count.
- `GET /api/documents/stats` — current vector collection size.
- `POST /api/query` — body: `query`, optional `query_type`, `equipment_id`, `standard`.
- `GET /api/maintenance/{equipment_id}` — equipment risk, failure window and matching work orders.
- `GET /api/compliance/audit/{standard}` — compliance matrix and counts.
- `GET /api/patterns` — recurring equipment/failure pairs.

Knowledge-query responses include `answer`, `citations`, `confidence`, and `follow_up_suggestions`.
