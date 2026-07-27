from __future__ import annotations

import os
from urllib.parse import quote

import pytest
from playwright.sync_api import APIRequestContext, Page, Playwright, expect

from pages.login_page import LoginPage
from pages.projects_page import ProjectsPage
from utils.browserstack import MobileCapability, connect_mobile_web
from utils.config import required_env
from utils.test_data import unique_project_data


@pytest.mark.integration
@pytest.mark.destructive
def test_project_creation_flow(
    api_context: APIRequestContext,
    page: Page,
    playwright: Playwright,
    settings,
    company1_token: str,
    company2_token: str,
):
    project = unique_project_data()
    project_id: int | None = None

    try:
        # 1. API: create data using the correct tenant identity.
        response = api_context.post(
            "/api/v1/projects",
            headers={
                "Authorization": f"Bearer {company1_token}",
                "X-Tenant-ID": "company1",
                "Idempotency-Key": project.name,
            },
            data={
                "name": project.name,
                "description": project.description,
                "team_members": project.team_members,
            },
        )
        assert response.status == 201, f"Create failed: {response.status} {response.text()}"
        body = response.json()
        project_id = body["id"]
        assert body["name"] == project.name
        assert body["status"] == "active"

        # Poll the read API until asynchronous indexing/read-model propagation is complete.
        expect.poll(
            lambda: api_context.get(
                f"/api/v1/projects/{project_id}",
                headers={
                    "Authorization": f"Bearer {company1_token}",
                    "X-Tenant-ID": "company1",
                },
            ).status,
            timeout=20_000,
        ).to_be(200)

        # 2. Web UI: log in to Company1 and validate user-visible content.
        company1_url = settings.tenant_base_url("company1")
        login = LoginPage(page, company1_url, settings.assertion_timeout_ms)
        projects = ProjectsPage(page, company1_url, settings.assertion_timeout_ms)
        login.open()
        login.login(
            required_env("COMPANY1_ADMIN_EMAIL"),
            required_env("COMPANY1_ADMIN_PASSWORD"),
            otp_code=os.getenv("E2E_2FA_BYPASS_TOKEN"),
        )
        projects.open()
        projects.expect_project_visible(project.name)

        # 3. Mobile web: run only when BrowserStack credentials are provided.
        if os.getenv("BROWSERSTACK_USERNAME") and os.getenv("BROWSERSTACK_ACCESS_KEY"):
            capability = MobileCapability(
                name=f"Project visible on mobile - {project.name}",
                device=os.getenv("BS_DEVICE", "Samsung Galaxy S23"),
                os_version=os.getenv("BS_OS_VERSION", "13.0"),
                browser=os.getenv("BS_MOBILE_BROWSER", "chrome"),
            )
            mobile_browser = connect_mobile_web(playwright, capability)
            try:
                mobile_context = mobile_browser.new_context()
                mobile_page = mobile_context.new_page()
                mobile_login = LoginPage(mobile_page, company1_url, settings.assertion_timeout_ms)
                mobile_projects = ProjectsPage(mobile_page, company1_url, settings.assertion_timeout_ms)
                mobile_login.open()
                mobile_login.login(
                    required_env("COMPANY1_ADMIN_EMAIL"),
                    required_env("COMPANY1_ADMIN_PASSWORD"),
                    otp_code=os.getenv("E2E_2FA_BYPASS_TOKEN"),
                )
                mobile_projects.open()
                mobile_projects.expect_project_visible(project.name)
                expect(mobile_page.locator("body")).not_to_have_class("horizontal-overflow")
            finally:
                mobile_browser.close()
        else:
            pytest.skip("BrowserStack credentials unavailable; API and desktop UI checks completed")

        # 4. Security: Company2 API must not read Company1's project.
        isolation_response = api_context.get(
            f"/api/v1/projects/{project_id}",
            headers={
                "Authorization": f"Bearer {company2_token}",
                "X-Tenant-ID": "company2",
            },
        )
        assert isolation_response.status in {403, 404}, (
            "Tenant isolation failure: Company2 could retrieve a Company1 project"
        )

        # Also verify absence from Company2's UI.
        company2_page = page.context.new_page()
        company2_url = settings.tenant_base_url("company2")
        company2_login = LoginPage(company2_page, company2_url, settings.assertion_timeout_ms)
        company2_projects = ProjectsPage(company2_page, company2_url, settings.assertion_timeout_ms)
        company2_login.open()
        company2_login.login(
            required_env("COMPANY2_USER_EMAIL"),
            required_env("COMPANY2_USER_PASSWORD"),
        )
        company2_projects.open()
        company2_projects.expect_project_absent(project.name)

    finally:
        # Cleanup is idempotent and runs even after UI/mobile/security failures.
        if project_id and os.getenv("KEEP_TEST_DATA", "false").lower() != "true":
            cleanup = api_context.delete(
                f"/api/v1/projects/{project_id}",
                headers={
                    "Authorization": f"Bearer {company1_token}",
                    "X-Tenant-ID": "company1",
                },
            )
            assert cleanup.status in {200, 202, 204, 404}, (
                f"Cleanup failed for project {project_id}: {cleanup.status}"
            )
