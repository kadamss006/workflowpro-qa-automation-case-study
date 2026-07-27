# WorkFlow Pro QA Automation Case Study

A case-study repository demonstrating flaky-test debugging, scalable framework design, API + UI integration testing, cross-browser execution, BrowserStack mobile concepts, CI/CD, and multi-tenant security validation.

## Deliverables
- Detailed flaky-test analysis: `docs/FLAKY_TEST_ANALYSIS.md`
- Framework design and missing requirements: `docs/FRAMEWORK_DESIGN.md`
- API + UI + mobile strategy: `docs/INTEGRATION_STRATEGY.md`
- Assumptions: `docs/ASSUMPTIONS.md`
- Corrected login tests: `tests/ui/test_login_reliable.py`
- Integrated project flow: `tests/integration/test_project_creation_flow.py`
- CI example: `.github/workflows/qa.yml`

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps
cp .env.example .env
```

Fill `.env` with non-production test credentials and tokens.

## Run examples

```bash
pytest -m smoke --browser=chromium
pytest -m integration --browser=chromium --html=reports/report.html --self-contained-html
pytest -m security --browser=firefox
pytest --browser=chromium --browser=firefox --browser=webkit
pytest -n auto -m regression
```

For BrowserStack mobile web, set `BROWSERSTACK_USERNAME`, `BROWSERSTACK_ACCESS_KEY`, and verified device capability values.

## Reliability choices
- Retryable Playwright expectations instead of fixed sleeps.
- Stable labels/test IDs instead of brittle CSS classes.
- Unique test data and `finally` cleanup.
- API polling for eventual consistency.
- Positive Company1 checks plus negative Company2 API/UI checks.
- Screenshot, video, trace, and HTML report support.
- Small PR matrix and broader nightly matrix to control cloud cost.

## Important note
This repository is an implementation-ready reference. Because the assessment does not provide a real WorkFlow Pro environment, several selectors, endpoints, status codes, and BrowserStack capabilities are documented assumptions and must be aligned with the actual product before execution.

## References used
- Playwright Python auto-waiting and web-first assertions: https://playwright.dev/python/docs/actionability
- Playwright Python pytest plugin: https://playwright.dev/python/docs/test-runners
- Playwright Python API testing: https://playwright.dev/python/docs/api-testing
- pytest fixtures and parameterization: https://docs.pytest.org/en/stable/how-to/fixtures.html
- BrowserStack Playwright Automate: https://www.browserstack.com/docs/automate/playwright
- BrowserStack Appium App Automate: https://www.browserstack.com/docs/app-automate/appium
