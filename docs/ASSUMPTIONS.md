# Assumptions

1. WorkFlow Pro is a fictional assessment application; URLs and credentials are placeholders.
2. Stable accessible labels or `data-testid` attributes can be added to the product.
3. Successful project creation returns HTTP 201; the prompt's sample body is authoritative but status code was not specified.
4. Project deletion exists at `DELETE /api/v1/projects/{id}` for test cleanup.
5. Project read exists at `GET /api/v1/projects/{id}` for eventual-consistency polling.
6. The API accepts JSON and supports an idempotency key; remove that header if unsupported.
7. Tenant ID must agree with token scope. Cross-tenant object access returns 403 or 404.
8. A dedicated staging environment and automation users exist.
9. 2FA is handled through a dedicated TOTP secret or security-approved E2E bypass, never through manual input in CI.
10. “Mobile” means mobile web for the Playwright example. Native/hybrid apps would use Appium on BrowserStack App Automate.
11. Exact BrowserStack device/OS capability values must be selected from the account's current capability builder.
12. BrowserStack mobile checks are conditional in the sample so reviewers can run the repository without paid credentials.
13. Company2 has at least one seeded project for the multi-tenant list test; otherwise that test should create its own Company2 fixture.
14. The application exposes a visible dashboard heading, welcome message, loading indicators, and project cards with stable test IDs.
15. Production data is never used by this suite.
