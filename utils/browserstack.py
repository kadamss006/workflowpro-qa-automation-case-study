from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.parse import quote

from playwright.sync_api import Browser, Playwright


@dataclass(frozen=True)
class MobileCapability:
    name: str
    device: str
    os_version: str
    browser: str


def connect_mobile_web(playwright: Playwright, capability: MobileCapability) -> Browser:
    """Connect Playwright to a BrowserStack real-mobile browser session.

    Capability names can change, so verify the exact device/OS combination in the
    BrowserStack capability builder before a real execution.
    """
    username = os.environ["BROWSERSTACK_USERNAME"]
    access_key = os.environ["BROWSERSTACK_ACCESS_KEY"]
    caps = {
        "browser": capability.browser,
        "os": "ios" if "iPhone" in capability.device else "android",
        "os_version": capability.os_version,
        "device": capability.device,
        "real_mobile": "true",
        "browserstack.username": username,
        "browserstack.accessKey": access_key,
        "browserstack.projectName": os.getenv("BROWSERSTACK_PROJECT", "WorkFlow Pro QA"),
        "browserstack.buildName": os.getenv("BROWSERSTACK_BUILD", "local"),
        "browserstack.sessionName": capability.name,
        "browserstack.local": os.getenv("BROWSERSTACK_LOCAL", "false"),
        "browserstack.debug": "true",
        "browserstack.networkLogs": "true",
        "browserstack.console": "errors",
    }
    ws_endpoint = "wss://cdp.browserstack.com/playwright?caps=" + quote(json.dumps(caps))
    return playwright.chromium.connect(ws_endpoint)
