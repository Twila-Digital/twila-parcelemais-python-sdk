from .api_error import ParceleMaisApiError
from .problem_details import ProblemDetails


class ParceleMaisValidationError(ParceleMaisApiError):
    def __init__(self, message: str, problem_details: ProblemDetails) -> None:
        super().__init__(message, 400, problem_details)
