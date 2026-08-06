# Security model

## Authentication sessions

When `OPSIQ_AUTH_REQUIRED=true`, login issues a short-lived access token and a refresh token. Every refresh token carries a cryptographically random `jti`; the SQLite operational store persists only its SHA-256 digest, user identity, expiry and revocation timestamps. Raw refresh tokens are never stored server-side.

Refresh is single-use. The backend validates signature, token type and expiry, verifies the user is active, then atomically revokes the presented session and creates its successor before returning a new access/refresh pair. Reusing a rotated or logged-out token returns `401`. Logout is idempotent for a valid signed token: repeated calls return success while its session stays revoked.

Administrators can revoke all sessions with `POST /api/auth/users/{username}/revoke-sessions`. `PATCH /api/auth/users/{username}` also revokes every active session when the account is disabled or its role changes. Any future password-change operation must use the same bulk-revocation method in the password-update transaction.

## Operational requirements

- Keep `OPSIQ_JWT_SECRET` outside Git and use at least 32 random characters.
- Persist `OPSIQ_DB_PATH` on the Railway `/data` volume; refresh sessions share this database.
- Remove the bootstrap administrator password after first initialization.
- Use HTTPS in production. Tokens are held in browser `sessionStorage` and must never appear in URLs or logs.
- Backend permission checks remain authoritative; frontend route and control visibility are UX safeguards only.

## Current limitations

SQLite session persistence is appropriate only for the single-instance demonstration. Multi-instance deployment requires a shared transactional store such as PostgreSQL. Expired/revoked session-row pruning, password change/reset, SSO, tenant isolation, rate limiting, CSRF-resistant cookie sessions, security-event export and formal penetration testing remain future hardening work.