import os
import pytest
from playwright.sync_api import expect

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from utils.config import required_env


@pytest.mark.smoke
@pytest.mark.parametrize("tenant,email_env,password_env", [
    ("company1", "COMPANY1_ADMIN_EMAIL", "COMPANY1_ADMIN_PASSWORD"),
    ("company2", "COMPANY2_USER_EMAIL", "COMPANY2_USER_PASSWORD"),
])
def test_user_login_is_reliable(page, settings, tenant, email_env, password_env):
    base_url = settings.tenant_base_url(tenant)
    login = LoginPage(page, base_url, settings.assertion_timeout_ms)
    dashboard = DashboardPage(page, settings.assertion_timeout_ms)

    login.open()
    login.login(
        required_env(email_env),
        required_env(password_env),
        otp_code=os.getenv("E2E_2FA_BYPASS_TOKEN"),
    )
    dashboard.wait_until_loaded()

    # URL assertion accepts a tenant-specific host and optional query parameters.
    expect(page).to_have_url(lambda url: url.startswith(base_url) and "/dashboard" in url)


@pytest.mark.security
def test_company2_user_only_sees_company2_projects(page, settings):
    base_url = settings.tenant_base_url("company2")
    login = LoginPage(page, base_url, settings.assertion_timeout_ms)
    dashboard = DashboardPage(page, settings.assertion_timeout_ms)

    login.open()
    login.login(required_env("COMPANY2_USER_EMAIL"), required_env("COMPANY2_USER_PASSWORD"))
    dashboard.wait_until_loaded()

    cards = dashboard.project_cards
    expect(cards.first).to_be_visible(timeout=settings.assertion_timeout_ms)
    card_count = cards.count()
    assert card_count > 0, "Expected seeded Company2 projects for this test account"

    # Stronger than checking branding text: verify each card exposes the expected tenant contract.
    for index in range(card_count):
        card = cards.nth(index)
        expect(card).to_have_attribute("data-tenant-id", "company2")
