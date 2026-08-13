from __future__ import annotations

from datetime import datetime
from typing import Protocol


class UtcClock(Protocol):
    def __call__(self) -> datetime:
        ...
