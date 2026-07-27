from __future__ import annotations

from playwright.sync_api import Page, expect


class ProjectsPage:
    def __init__(self, page: Page, base_url: str, assertion_timeout_ms: int = 15000):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.timeout = assertion_timeout_ms
        self.loading_indicator = page.get_by_test_id("projects-loading")
        self.project_cards = page.get_by_test_id("project-card")

    def open(self) -> None:
        self.page.goto(f"{self.base_url}/projects", wait_until="domcontentloaded")
        if self.loading_indicator.count() > 0:
            expect(self.loading_indicator).to_be_hidden(timeout=self.timeout)

    def expect_project_visible(self, project_name: str) -> None:
        target = self.project_cards.filter(has_text=project_name)
        expect(target).to_have_count(1, timeout=self.timeout)
        expect(target).to_be_visible(timeout=self.timeout)

    def expect_project_absent(self, project_name: str) -> None:
        expect(self.project_cards.filter(has_text=project_name)).to_have_count(0, timeout=self.timeout)
