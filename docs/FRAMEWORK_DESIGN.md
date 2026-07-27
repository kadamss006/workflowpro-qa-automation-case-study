# Part 2 - Framework Design

## Architecture

```text
workflowpro_qa_submission/
├── config/                 # environment and execution matrix
├── data/                   # templates only; secrets remain outside Git
├── docs/                   # test plan, analysis, assumptions
├── pages/                  # page objects / user-facing workflows
├── tests/
│   ├── api/                # service contract and validation tests
│   ├── ui/                 # browser tests
│   ├── integration/        # API-created data verified through UI/mobile
│   └── security/           # tenant and authorization checks
├── utils/                  # configuration, data factory, retry, BrowserStack
├── reports/                # generated artifacts (normally gitignored)
├── .github/workflows/      # CI pipeline
├── conftest.py             # shared pytest fixtures/hooks
└── pytest.ini              # markers and defaults
```

## Core design decisions

### 1. Pytest as orchestrator
Fixtures provide isolated browser contexts, API clients, identities, configuration, and teardown. Markers split smoke, regression, integration, security, mobile, and destructive suites. Parameterization expands roles, tenants, browsers, and negative inputs without copying test logic.

### 2. Playwright for web and API
Playwright covers Chromium, Firefox, and WebKit, provides auto-waiting locators, retrying web assertions, tracing, screenshots, and an API request context. API tests create deterministic state faster than UI setup; UI tests validate the user-visible result.

### 3. Page objects plus task-level workflows
Page objects store selectors and page-specific behavior. Authentication and project workflows can later become service/task objects when repeated across desktop and mobile. Assertions remain near tests for business readability, except reusable component readiness checks.

### 4. Mobile split
- Mobile web: Playwright against BrowserStack real/mobile browsers.
- Native/hybrid app: Appium + BrowserStack App Automate in a separate adapter/test package because Playwright is a browser tool and should not be forced into native-app automation.

### 5. Configuration precedence
Defaults in YAML -> environment-specific YAML -> environment variables/CI secrets -> command-line pytest options. No secret is committed. Tenant URL is built from tenant + base domain. Browser/device matrices are selected by pipeline type.

### 6. Test data strategy
Use API factories and unique IDs. Prefer one logical dataset per test worker. Maintain dedicated seeded reference data for read-only tests. Use `finally` cleanup and idempotent delete. Tag automation-created objects with a prefix and run a scheduled janitor as a safety net. Never share mutable project records across parallel tests.

### 7. Parallel execution
Use pytest-xdist at test level after confirming backend rate limits and data isolation. Partition BrowserStack runs according to licensed parallel sessions. Avoid parallelizing tests that mutate the same user/tenant unless each worker receives a separate account or namespace.

### 8. Reporting and observability
HTML/Allure reports include environment, build, browser/device, tenant alias, and test-data ID. Capture trace, screenshot, video, console, and network logs on failure. Track flake rate separately from product failures; quarantine requires owner, issue, and expiry date.

## Suggested base abstractions

```python
class TenantSession:
    tenant_id: str
    base_url: str
    token: str
    role: str

class ApiClient:
    def create_project(self, tenant_session, project_data): ...
    def get_project(self, tenant_session, project_id): ...
    def delete_project(self, tenant_session, project_id): ...

class AuthWorkflow:
    def login(self, page, tenant_session, otp_provider=None): ...

class ProjectFactory:
    def build_unique(self): ...
    def cleanup(self): ...
```

## Missing requirements / questions

### Product and platforms
1. Is “mobile” responsive web, native iOS/Android, or both?
2. Which OS/browser/device versions are officially supported and what usage analytics define the priority matrix?
3. Are Safari requirements satisfied by WebKit locally, or is real macOS Safari mandatory?
4. Are there region, locale, timezone, accessibility, or offline requirements?

### Authentication and security
5. Which users require 2FA, and is a seeded TOTP secret or approved E2E bypass available?
6. Does tenant identity come from subdomain, token claims, header, database mapping, or all of them?
7. Should unauthorized object access return 403 or 404?
8. Are SSO, password expiry, account lockout, and session timeout in scope?

### Data and environments
9. Is there a dedicated test environment and reset/cleanup API?
10. Can tests create tenants/users, or are accounts centrally seeded?
11. What are API rate limits and asynchronous consistency expectations?
12. Can third-party integrations use sandboxes/mocks, and who owns their availability?
13. Is production smoke testing allowed, and what operations are prohibited?

### Execution and reporting
14. Required pull-request duration and release gate?
15. BrowserStack parallel-session allowance and monthly budget?
16. Which CI system, source control, and reporting dashboard are required?
17. Retention period for videos/traces and handling of sensitive data in artifacts?
18. Required flake-rate and pass-rate service-level objectives?
19. Who triages failures and how are quarantined tests governed?
20. What performance, load, and accessibility standards are expected?
