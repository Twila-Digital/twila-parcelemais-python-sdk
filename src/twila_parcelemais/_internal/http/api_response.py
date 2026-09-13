from dataclasses import dataclass
from typing import Any


@dataclass
class ApiResponse:
    status_code: int
    body: Any
    headers: dict[str, str]
