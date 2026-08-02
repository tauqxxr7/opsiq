# OPSIQ RBAC validation

Validation date: 2 August 2026
Branch: `feat/enterprise-frontend-redesign`

## Method

The canonical matrix in `backend/core/permissions.py` was exercised for every permission and all eight roles. FastAPI dependency tests verify that every protected `/api` endpoint declares a canonical permission. Existing lifecycle tests also issue real JWTs against persistent incident, work-order and user endpoints.

## Observed operational action matrix

Status order: read incidents / create incident / update incident / create work order / update work order / approve / complete / list users.

| Role | Additional frontend routes | Actual HTTP status observed |
|---|---|---|
| Operator | None | `200 / 201 / 403 / 403 / 403 / 403 / 403 / 403` |
| Maintenance Engineer | None | `200 / 403 / 200 / 201 / 200 / 403 / 200 / 403` |
| Reliability Engineer | `/patterns`, `/benchmarks` | `200 / 403 / 200 / 201 / 403 / 403 / 403 / 403` |
| Safety Engineer | `/compliance` | `200 / 201 / 200 / 403 / 403 / 403 / 403 / 403` |
| Supervisor | `/compliance`, `/patterns`, `/audit` | `200 / 201 / 200 / 201 / 200 / 200 / 200 / 403` |
| Plant Manager | `/compliance`, `/patterns`, `/audit` | `200 / 201 / 200 / 201 / 200 / 200 / 200 / 403` |
| Administrator | `/compliance`, `/patterns`, `/benchmarks`, `/audit`, `/settings` | `200 / 201 / 200 / 201 / 200 / 200 / 200 / 200` |
| Auditor | `/compliance`, `/patterns`, `/benchmarks`, `/audit` | `200 / 403 / 403 / 403 / 403 / 403 / 403 / 403` |

The canonical permission test additionally verifies all eight roles across general read, compliance read, pattern read, benchmark execution, audit read, document upload, incident create/update, work-order create/update/approve/complete and user administration.

## Corrected alignment results

- Sidebar and command-palette entries are now hidden when the current role cannot access the route.
- Route guards remain active and direct forbidden navigation renders a professional HTTP 403 page.
- Specialist compliance, pattern, benchmark and audit APIs now use the same role sets as their frontend routes.
- Document upload, incident creation, work-order generation/persistence and approval buttons are hidden for unauthorized roles.
- Every protected backend endpoint has an explicit named permission dependency; backend enforcement remains authoritative.
- Missing or invalid authentication returns `401`; authenticated requests without permission return `403`.
- Administrator controls do not render while identity resolution is pending or for non-administrators.

## Authentication and persistence regression results

| Scenario | Expected and observed result |
|---|---|
| Valid login | `200` with access and refresh tokens |
| Invalid password | `401` |
| Missing token | `401` |
| Valid refresh | `200` |
| Expired access token | `401` |
| Unauthorized authenticated role | `403` |
| SQLite process restart | Incident, approved linked work order and created user persist |

Logout still clears session tokens client-side; refresh-token revocation remains a documented future hardening item and is not an RBAC alignment mismatch.

See `docs/PERMISSION_MODEL.md` for the complete route and endpoint model.
