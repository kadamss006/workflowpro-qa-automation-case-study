# WorkFlow Pro QA Automation Test Plan

## 1. Objective
Validate critical B2B SaaS workflows across API, desktop browsers, mobile web, roles, and tenant boundaries while producing deterministic diagnostics suitable for CI/CD.

## 2. Scope
In scope: login, conditional 2FA, dashboard loading, project creation and display, role permissions, API contracts, tenant isolation, Chrome/Firefox/WebKit, representative Android Chrome and iOS Safari sessions, CI reporting, cleanup, and failure artifacts.

Out of scope until clarified: native application automation, billing/payment providers, destructive production testing, deep performance benchmarking, accessibility conformance target, and third-party sandbox ownership.

## 3. Test levels
- API contract tests: fastest feedback for status, schema, validation, authorization, and tenant checks.
- UI smoke tests: critical login and project visibility on Chromium for each pull request.
- Cross-browser regression: Firefox and WebKit nightly or before release.
- Mobile web: small risk-based BrowserStack matrix nightly/release; native apps would use Appium separately.
- Security-focused functional checks: token/header mismatch, object-level authorization, enumeration resistance, and cross-tenant UI absence.

## 4. Entry criteria
Stable staging environment, seeded users per tenant/role, API tokens or supported login API, deterministic 2FA strategy, test-id contracts, BrowserStack credentials, cleanup endpoint, and known deployment version.

## 5. Exit criteria
All critical smoke tests pass; no confirmed tenant-isolation defect; failed non-critical tests are triaged; artifacts are attached; flaky test rate remains below agreed threshold; cleanup succeeds.

## 6. Risks and mitigations
- Asynchronous propagation: poll a business condition with a bounded timeout.
- Shared test data: generate unique records and delete in `finally`.
- 2FA: use dedicated test account, seeded TOTP secret, or environment-scoped bypass approved by security.
- BrowserStack cost: PRs on Chromium, nightly representative cross-browser/mobile matrix, full matrix only before release.
- Third-party outages: classify and quarantine external dependency failures; do not hide product defects with broad retries.
- Tenant leakage: verify API response and UI absence using both positive and negative identities.

## 7. Reporting
Generate pytest HTML and optional Allure reports. Retain screenshots, trace, video, console/network logs on failure. Trend pass rate, duration, flake rate, failure category, and browser/device distribution.
