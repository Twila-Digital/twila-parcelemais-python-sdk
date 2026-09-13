from typing import Any, Optional

from .base import ParceleMaisError
from .problem_details import ProblemDetails


class ParceleMaisApiError(ParceleMaisError):
    def __init__(self, message: str, status_code: int, problem_details: ProblemDetails) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.problem_details = problem_details

    @property
    def error_code(self) -> Optional[str]:
        return self.problem_details.type

    @property
    def field_errors(self) -> Optional[dict[str, Any]]:
        return self.problem_details.errors

    @property
    def correlation_id(self) -> Optional[str]:
        return self.problem_details.correlation_id
