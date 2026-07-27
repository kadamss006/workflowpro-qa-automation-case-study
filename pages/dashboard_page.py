from __future__ import annotations

from playwright.sync_api import Page, expect


class DashboardPage:
    def __init__(self, page: Page, assertion_timeout_ms: int = 15000):
        self.page = page
        self.timeout = assertion_timeout_ms
        self.heading = page.get_by_role("heading", name="Dashboard")
        self.welcome_message = page.get_by_test_id("welcome-message")
        self.loading_indicator = page.get_by_test_id("dashboard-loading")
        self.project_cards = page.get_by_test_id("project-card")

    def wait_until_loaded(self) -> None:
        expect(self.page).to_have_url(lambda url: "/dashboard" in url, timeout=self.timeout)
        expect(self.heading).to_be_visible(timeout=self.timeout)
        if self.loading_indicator.count() > 0:
            expect(self.loading_indicator).to_be_hidden(timeout=self.timeout)
        expect(self.welcome_message).to_be_visible(timeout=self.timeout)

    def project_card(self, project_name: str):
        return self.project_cards.filter(has_text=project_name)

    def expect_project_visible(self, project_name: str) -> None:
        card = self.project_card(project_name)
        expect(card).to_have_count(1, timeout=self.timeout)
        expect(card).to_be_visible(timeout=self.timeout)

    def expect_project_absent(self, project_name: str) -> None:
        expect(self.project_card(project_name)).to_have_count(0, timeout=self.timeout)
