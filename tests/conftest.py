from __future__ import annotations

import os
from pathlib import Path

import pytest
from playwright.sync_api import APIRequestContext, Browser, BrowserContext, Page, Playwright

from utils.config import load_settings, required_env


@pytest.fixture(scope="session")
def settings():
    return load_settings()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {**browser_type_launch_args, "headless": True}


@pytest.fixture
def context(browser: Browser, settings) -> BrowserContext:
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        locale="en-US",
        timezone_id="Asia/Kolkata",
        ignore_https_errors=settings.env != "production",
        record_video_dir="reports/videos",
    )
    context.set_default_timeout(settings.assertion_timeout_ms)
    context.set_default_navigation_timeout(settings.navigation_timeout_ms)
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext, request) -> Page:
    page = context.new_page()
    yield page
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        Path("reports/screenshots").mkdir(parents=True, exist_ok=True)
        safe_name = request.node.nodeid.replace("/", "_").replace("::", "__")
        page.screenshot(path=f"reports/screenshots/{safe_name}.png", full_page=True)
        context.tracing.stop(path=f"reports/{safe_name}-trace.zip")


@pytest.fixture(autouse=True)
def start_trace(context: BrowserContext):
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield


@pytest.fixture(scope="session")
def api_context(playwright: Playwright, settings) -> APIRequestContext:
    context = playwright.request.new_context(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout_seconds * 1000,
        extra_http_headers={"Accept": "application/json"},
    )
    yield context
    context.dispose()


@pytest.fixture
def company1_token() -> str:
    return required_env("COMPANY1_API_TOKEN")


@pytest.fixture
def company2_token() -> str:
    return required_env("COMPANY2_API_TOKEN")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)
