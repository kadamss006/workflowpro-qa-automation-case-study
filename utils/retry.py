from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry_transient(
    operation: Callable[[], T],
    *,
    attempts: int = 3,
    initial_delay_seconds: float = 0.5,
    retry_on: tuple[type[BaseException], ...] = (ConnectionError, TimeoutError),
) -> T:
    """Retry only transient infrastructure failures, never assertion failures."""
    delay = initial_delay_seconds
    last_error: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except retry_on as exc:
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(delay)
            delay *= 2
    assert last_error is not None
    raise last_error
