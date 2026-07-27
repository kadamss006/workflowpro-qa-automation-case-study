# Part 1 - Flaky Test Debugging

## Problems in the original tests

1. **Immediate URL equality after click.** The assertion runs before navigation, redirect, token exchange, or dashboard rendering completes. Exact equality also fails for a trailing slash, tenant subdomain, query string, locale, or SSO callback.
2. **Non-retrying visibility check.** `is_visible()` answers immediately; it does not provide a web-first assertion that retries until the element becomes visible.
3. **Dynamic content is not synchronized.** The dashboard and project cards load asynchronously, but the test never waits for a stable user-visible condition or loading indicator to disappear.
4. **Conditional 2FA is ignored.** A user may be routed to a verification step instead of the dashboard.
5. **Hard-coded production-like URL and credentials.** This prevents safe environment separation, leaks secrets, and can collide with real data or security policies.
6. **CSS selectors are implementation-coupled.** IDs/classes may be changed by frontend refactoring. Accessible roles, labels, and dedicated `data-testid` contracts are more stable.
7. **No assertion that the login page itself loaded.** Form actions may race with redirects, cookie banners, service workers, or partial page hydration.
8. **No explicit browser/context configuration.** CI screen size, locale, timezone, HTTPS certificates, and headless behavior can differ from local execution.
9. **Manual Playwright lifecycle inside every test.** Repeated setup makes diagnostics and cleanup inconsistent. The pytest plugin provides isolated fixtures and easier multi-browser execution.
10. **Browser closes only on the happy path.** An assertion failure can skip `browser.close()`, leaking processes and affecting later tests.
11. **`.all()` snapshots elements too early.** The list is captured before dynamic project cards finish loading, potentially returning zero or an incomplete collection.
12. **Weak tenant assertion.** Checking whether visible text contains “Company2” is not a reliable security check. Project names may not contain a tenant label, and hidden or leaked records may pass/fail incorrectly.
13. **No seeded-data contract.** The test assumes Company2 already has projects, but zero cards makes the loop pass vacuously.
14. **No role/tenant identity validation.** It does not verify the authenticated user's tenant, host, API scope, or authorization behavior.
15. **No diagnostics.** There are no screenshots, trace, video, console logs, network logs, or response details on failure.
16. **No transient network strategy.** Navigation and API calls can fail from DNS, proxy, or service startup issues, but indiscriminate retries would also hide real defects.
17. **No test isolation or cleanup.** Shared sessions/data can influence order-dependent results.
18. **Single-browser local assumption.** The requirements state different browsers and screen sizes, but the code launches only default Chromium.
19. **No timeout strategy.** Default timeouts may be too short for slow tenants or too long to diagnose a genuine hang.
20. **Potential popup/consent/interstitial handling gap.** Cookie consent, maintenance banners, password-expiry screens, or first-login tours can block controls in CI test accounts.

## Why CI fails more often than local
CI agents usually have lower or bursty CPU, shared network capacity, colder caches, headless rendering, clean cookies, different DNS/proxy/TLS settings, and parallel tests competing for the same tenant data. A local developer often has a warm browser profile, cached assets, stable credentials, a familiar viewport, and may unconsciously wait before observing the result. Cross-browser engines also differ in timing and layout. These conditions expose race conditions that exact, immediate assertions conceal locally.

## Reliability principles used in the correction
- Wait for business outcomes, not fixed sleeps.
- Use Playwright locators and retrying `expect` assertions.
- Model 2FA explicitly.
- Use pytest fixtures for lifecycle and isolation.
- Use stable semantic selectors/test IDs.
- Assert non-empty seeded data before iterating.
- Validate tenant identity through a stable contract and negative tests.
- Capture failure artifacts.
- Retry only known transient infrastructure operations; never retry assertions to manufacture a pass.
- Parameterize browser/environment/tenant instead of hard-coding.

The corrected implementation is in `tests/ui/test_login_reliable.py`, supported by `pages/login_page.py`, `pages/dashboard_page.py`, and `tests/conftest.py`.
