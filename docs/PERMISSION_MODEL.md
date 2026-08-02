# OPSIQ permission model

The canonical authorization policy is `backend/core/permissions.py`. Every protected FastAPI endpoint declares one named permission through `authorize(...)`. The frontend mirrors route and action visibility in `frontend/src/auth/permissions.js`; this mirror improves UX only. FastAPI remains authoritative and returns `401` for missing or invalid authentication and `403` for an authenticated role without the required permission.

Role abbreviations: **OP** Operator, **ME** Maintenance Engineer, **RE** Reliability Engineer, **SE** Safety Engineer, **SV** Supervisor, **PM** Plant Manager, **AD** Administrator, **AU** Auditor. **All** means all eight authenticated roles.

| Route | API endpoint | Read roles | Create roles | Update roles | Approve roles | Complete/close roles | Administrative roles |
|---|---|---|---|---|---|---|---|
| `/dashboard` | `/api/sensors/*`, `/api/maintenance`, `/api/analytics/*`, `/api/documents/stats` | All | - | - | - | - | - |
| `/assets` | `/api/sensors/live/{id}`, `/trend/{id}`, `/fleet/status`, `/alarms/active` | All | - | - | - | - | - |
| `/copilot` | `POST /api/query` | All | - | - | - | - | - |
| `/maintenance` | `/api/maintenance`, `/api/maintenance/{id}`, `/incidents/similar` | All | Work-order draft: ME, RE, SV, PM, AD | - | - | - | - |
| `/incidents` | `GET /api/incidents`, `GET /api/incidents/{id}` | All | OP, SE, SV, PM, AD | ME, RE, SE, SV, PM, AD | - | Same as update through incident status | - |
| `/reliability` | `/api/analytics/reliability`, `/downtime/trends` | All | - | - | - | - | - |
| `/compliance` | `/api/compliance/audit/{standard}` | SE, SV, PM, AD, AU | - | - | - | - | - |
| `/work-orders` | `GET /api/work-orders`, `GET /api/work-orders/{id}` | All | ME, RE, SV, PM, AD | ME, SV, PM, AD | SV, PM, AD | ME, SV, PM, AD | - |
| `/patterns` | `GET /api/patterns` | RE, SV, PM, AD, AU | - | - | - | - | - |
| `/documents` | `GET /api/documents`, `/stats`; `POST /upload` | All | Upload: ME, RE, SE, SV, PM, AD | - | - | - | - |
| `/benchmarks` | `GET /api/benchmark/run` | RE, AD, AU | - | - | - | - | - |
| `/audit` | `GET /api/audit/recent` | SV, PM, AD, AU | - | - | - | - | - |
| `/settings` | `/api/auth/users*`; `GET /api/auth/roles` | AD for users; All for role identity | User: AD | User role/active: AD | - | - | Session revocation: AD |
| `/architecture` | None | All | - | - | - | - | - |

## Enforcement behavior

- Login, token refresh and refresh-token logout are public transport endpoints; refresh and logout still require a valid signed refresh token.
- Every other `/api` operation carries an explicit canonical permission dependency.
- Sidebar and command-palette entries are filtered by the signed-in role.
- Direct navigation remains protected and renders a dedicated 403 workspace.
- Incident creation, document upload, work-order generation/persistence and approval controls are hidden when the current role lacks the corresponding permission.
- Hidden controls are not a security boundary; direct requests are independently authorized by FastAPI.
- Administrator controls are rendered only after identity resolution and a successful route permission check.

## Change control

Permission changes must begin in `backend/core/permissions.py`, be reflected in the frontend UX mirror, and update the eight-role matrix tests and this document in the same change. Do not broaden a backend role set merely to match a visible frontend control.