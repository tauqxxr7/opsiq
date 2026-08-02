# OPSIQ RBAC validation

Release-candidate audit: 2 August 2026
Branch: `feat/enterprise-frontend-redesign`
Audited head: `cb32508907b99e221b2a67943827a791707a9888`

## Scope and method

The public Vercel preview was checked first. It renders the SPA but is built with authentication disabled (`Local development / Administrator`) and cannot currently reach Railway, so public login and role switching could not be verified. The HTTP matrix below was therefore executed against the feature-branch FastAPI app using a fresh SQLite database per role, real scrypt password hashes, issued JWTs and `TestClient`. The restart check reopened the same SQLite file in a new `OperationalStore` instance.

Common frontend routes for every authenticated role are `/dashboard`, `/assets`, `/copilot`, `/maintenance`, `/incidents`, `/reliability`, `/work-orders`, `/documents` and `/architecture`. The table lists additional guarded workspaces.

## Observed role matrix

Status order in the final column: read incidents / create incident / update incident / create work order / update work order / approve / complete / list users.

| Role | Additional accessible routes | Allowed actions | Denied actions | Actual HTTP status observed |
|---|---|---|---|---|
| Operator | None | Read; create incident | Update incident; create/update/approve/complete work order; user administration | `200 / 201 / 403 / 403 / 403 / 403 / 403 / 403` |
| Maintenance Engineer | None | Read; update incident; create/update/complete work order | Create incident; approve work order; user administration | `200 / 403 / 200 / 201 / 200 / 403 / 200 / 403` |
| Reliability Engineer | `/patterns`, `/benchmarks` | Read; update incident; create work order | Create incident; update/approve/complete work order; user administration | `200 / 403 / 200 / 201 / 403 / 403 / 403 / 403` |
| Safety Engineer | `/compliance` | Read; create/update incident | Work-order mutation; user administration | `200 / 201 / 200 / 403 / 403 / 403 / 403 / 403` |
| Supervisor | `/compliance`, `/patterns`, `/audit` | Read; create/update incident; create/update/approve/complete work order | User administration | `200 / 201 / 200 / 201 / 200 / 200 / 200 / 403` |
| Plant Manager | `/compliance`, `/patterns`, `/audit` | Read; create/update incident; create/update/approve/complete work order | User administration | `200 / 201 / 200 / 201 / 200 / 200 / 200 / 403` |
| Administrator | `/compliance`, `/patterns`, `/benchmarks`, `/audit`, `/settings` | All tested actions, including user administration | None in tested matrix | `200 / 201 / 200 / 201 / 200 / 200 / 200 / 200` |
| Auditor | `/compliance`, `/patterns`, `/benchmarks`, `/audit` | Read only | All incident/work-order mutations; user administration | `200 / 403 / 403 / 403 / 403 / 403 / 403 / 403` |

## Authentication results

| Scenario | Observed result |
|---|---|
| Valid username and password | `200` with access and refresh tokens |
| Invalid password | `401` |
| Protected endpoint without token | `401` |
| Refresh with valid refresh token | `200` |
| Expired access token | `401` |
| Logout | Frontend clears session tokens and returns to the login state when auth is enabled; no server-side token revocation endpoint exists |

## Persistence results

A test Administrator created an incident, created and approved its linked work order, and created an Auditor user. After closing the client and reopening the same SQLite database, all three records remained; the work order remained `APPROVED`. This validates process-restart persistence against one database file, not Railway volume attachment.

## Frontend/backend enforcement mismatches

- The sidebar and command palette show every navigation item to every role. A denied role sees `Access restricted` only after opening a guarded route. Backend mutation permissions still return `403`, but frontend visibility is not least-privilege.
- Specialist read APIs are authenticated but are not restricted to the same role lists as `/compliance`, `/patterns`, `/benchmarks` and `/audit`. A user denied the workspace can call those APIs directly once authenticated. This is an enforcement mismatch requiring an explicit product-policy decision before release.
- Logout clears browser session tokens but does not revoke an already-issued refresh token. Token expiry is the only server-side invalidation mechanism currently implemented.

## Release blockers

- Preview `VITE_AUTH_REQUIRED` is not enabled, so protected-route redirect, browser login, refresh, logout and all eight frontend role states are not production-like.
- Preview-to-Railway requests fail and every API-backed workspace reports the backend unavailable; updated CORS was not effective for the immutable preview origin at audit time.
- Railway `/data` volume attachment and persistence across an actual Railway restart could not be observed with the available access.

**RBAC release status: blocked for preview acceptance; backend permission matrix passes locally.**
