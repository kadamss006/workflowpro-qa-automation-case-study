from __future__ import annotations

from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page, base_url: str, assertion_timeout_ms: int = 15000):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.timeout = assertion_timeout_ms
        self.email = page.get_by_label("Email")
        self.password = page.get_by_label("Password")
        self.login_button = page.get_by_role("button", name="Log in")
        self.otp = page.get_by_label("Verification code")
        self.verify_button = page.get_by_role("button", name="Verify")

    def open(self) -> None:
        self.page.goto(f"{self.base_url}/login", wait_until="domcontentloaded")
        expect(self.login_button).to_be_visible(timeout=self.timeout)

    def login(self, email: str, password: str, otp_code: str | None = None) -> None:
        self.email.fill(email)
        self.password.fill(password)
        self.login_button.click()

        # Support both normal login and conditional 2FA.
        if self.otp.is_visible(timeout=2500):
            if not otp_code:
                raise RuntimeError("2FA challenge appeared but no OTP/bypass code was supplied")
            self.otp.fill(otp_code)
            self.verify_button.click()
