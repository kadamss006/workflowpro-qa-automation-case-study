from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    env: str
    base_domain: str
    api_base_url: str
    navigation_timeout_ms: int
    assertion_timeout_ms: int
    api_timeout_seconds: int
    secure: bool

    def tenant_base_url(self, tenant: str) -> str:
        scheme = "https" if self.secure else "http"
        return f"{scheme}://{tenant}.{self.base_domain}"


def load_settings() -> Settings:
    config = yaml.safe_load((ROOT / "config" / "settings.yaml").read_text(encoding="utf-8"))
    env = os.getenv("ENV", "staging")
    env_cfg = config["environments"][env]
    defaults = config["defaults"]
    return Settings(
        env=env,
        base_domain=os.getenv("BASE_DOMAIN", env_cfg["base_domain"]),
        api_base_url=os.getenv("API_BASE_URL", env_cfg["api_base_url"]),
        navigation_timeout_ms=int(defaults["navigation_timeout_ms"]),
        assertion_timeout_ms=int(defaults["assertion_timeout_ms"]),
        api_timeout_seconds=int(defaults["api_timeout_seconds"]),
        secure=bool(env_cfg["secure"]),
    )


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value
