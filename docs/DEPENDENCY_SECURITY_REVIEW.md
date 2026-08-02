# Dependency Security Review

Reviewed: 2026-08-02

The lockfile resolves React Router to 6.30.4, Vite to 5.4.21 and esbuild to 0.21.5. `npm audit --json` currently reports zero vulnerabilities, but the July 2026 React Router notices are assessed explicitly because registry audit data may lag published advisories.

## React Router open redirect — GHSA-wrjc-x8rr-h8h6

- **Package / installed:** `react-router` 6.30.4, via `react-router-dom` 6.30.4
- **Affected range:** `>=6.0.0 <7.18.0`
- **Exploit conditions:** attacker-supplied navigation containing backslashes reaches `<Link>` or `useNavigate`; user interaction is required and may navigate to an attacker-controlled origin.
- **Production deployment:** potentially affected because the code ships in the SPA. No exploitable flow was found: OPSIQ uses fixed internal navigation targets and does not navigate to API or query-string values.
- **Patched version:** 7.18.0
- **Migration impact:** breaking React Router 6-to-7 migration affecting route behavior and compatibility assumptions.
- **Tests after upgrade:** lint/build; all direct routes and legacy redirects; login return and role guards; malicious backslash, protocol-relative and absolute navigation cases; SPA rewrite checks.
- **Recommendation:** **defer with documented risk**. Keep destinations fixed/allowlisted and schedule a dedicated React Router 7 migration.

Source: https://github.com/advisories/GHSA-wrjc-x8rr-h8h6

## React Router SSR constructor injection — GHSA-337j-9hxr-rhxg

- **Package / installed:** `react-router` 6.30.4
- **Affected range:** `>=6.4.0 <7.18.0`
- **Exploit conditions:** Framework/Data Mode with manual SSR/hydration and application code allowing attacker input to overwrite serialized SSR errors.
- **Production deployment:** not affected by the current client-rendered declarative `BrowserRouter` architecture; OPSIQ performs no React Router SSR or hydration.
- **Patched version:** 7.18.0
- **Migration impact:** breaking router major upgrade; the SSR-only fix does not justify an unplanned migration for this SPA.
- **Tests after upgrade:** lint/build, all routes/direct refreshes and protected redirects; SSR serialization/hydration tests if the architecture later changes.
- **Recommendation:** **defer with documented risk** and reassess immediately if SSR or Framework/Data Mode is adopted.

Source: https://github.com/advisories/GHSA-337j-9hxr-rhxg

## esbuild development-server exposure — GHSA-67mh-4wv8-2f99

- **Package / installed:** `esbuild` 0.21.5, transitive through Vite 5.4.21
- **Affected range:** `<=0.24.2`
- **Exploit conditions:** a developer runs the development server and visits an attacker-controlled site, which can issue and read cross-origin development-server requests. Public network binding increases exposure.
- **Production deployment:** not affected. Vercel serves static build output and does not run Vite's development server.
- **Patched version:** esbuild 0.25.0; the current Vite dependency graph does not select it.
- **Migration impact:** supported remediation requires a Vite major upgrade. Forcing an unsupported transitive override could destabilize builds.
- **Tests after upgrade:** clean install, lint/build, HMR/source maps, all routes, local SPA fallback, deployment checks and Vercel preview build.
- **Recommendation:** **defer with documented risk** pending a planned Vite upgrade. Bind development to loopback, never expose it publicly and avoid untrusted sites while it runs.

Source: https://github.com/advisories/GHSA-67mh-4wv8-2f99

## Decision

No dependency was changed. Every published patch requires a breaking major upgrade in the current graph. Compensating controls are fixed internal navigation, no SSR, loopback-only development, static production hosting and deployment regression checks.
