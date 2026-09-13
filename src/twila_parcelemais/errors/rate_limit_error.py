from typing import Optional

from .api_error import ParceleMaisApiError
from .problem_details import ProblemDetails


class ParceleMaisRateLimitError(ParceleMaisApiError):
    def __init__(self, message: str, problem_details: ProblemDetails, retry_after_ms: Optional[int] = None) -> None:
        super().__init__(message, 429, problem_details)
        self.retry_after_ms = retry_after_ms
