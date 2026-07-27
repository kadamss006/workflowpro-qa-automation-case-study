# Part 3 - API + UI Integration Strategy

## Flow
1. Generate a globally unique project payload.
2. Create the project through `POST /api/v1/projects` with Company1 token and tenant header.
3. Validate the response contract and store the returned ID.
4. Poll the read API for asynchronous propagation instead of sleeping.
5. Log in to Company1 web UI and verify exactly one matching project card.
6. When BrowserStack credentials exist, repeat the user-visible validation on a representative real mobile browser.
7. Attempt to access the project using Company2 credentials and header; require 403/404.
8. Log in to Company2 UI and verify the project is absent.
9. Delete the project in `finally`, allowing idempotent 404.

## Edge-case handling
- Network failures: bounded retries only for connection/timeout failures; response failures are asserted immediately.
- Slow tenants: configuration-based navigation/assertion timeouts and condition polling.
- Eventual consistency: poll the resource/read model rather than use a fixed delay.
- Duplicate execution: unique names plus an idempotency key.
- Mobile responsiveness: validate visibility, viewport usability, and absence of known horizontal-overflow state; add screenshots and visual checks for critical breakpoints.
- 2FA: dedicated test account, TOTP secret, or approved environment bypass.
- Cleanup failure: reported as a failure and supported by a tagged-data janitor.
- BrowserStack unavailable: local API and desktop validation still execute; mobile is marked skipped rather than falsely passed.

## Security expectations
Tenant isolation is tested at both object API and UI levels. A negative result should not expose project metadata in response body, page source, client-side state, or network responses. A production framework would additionally inspect API responses and browser network logs for leaked identifiers.

The reference implementation is `tests/integration/test_project_creation_flow.py`.
