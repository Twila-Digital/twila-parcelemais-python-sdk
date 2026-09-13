from datetime import datetime, timezone
from typing import Optional

from .._internal.http.api_response import ApiResponse
from .api_error import ParceleMaisApiError
from .authentication_error import ParceleMaisAuthenticationError
from .base import ParceleMaisError
from .problem_details import parse_problem_details
from .rate_limit_error import ParceleMaisRateLimitError
from .validation_error import ParceleMaisValidationError


def exception_from_response(response: ApiResponse) -> ParceleMaisError:
    problem_details = parse_problem_details(response.body)
    message = problem_details.detail or problem_details.title or f"A API do Parcele+ retornou {response.status_code}."

    if response.status_code == 401:
        return ParceleMaisAuthenticationError(message)

    if response.status_code == 400 and problem_details.errors:
        return ParceleMaisValidationError(message, problem_details)

    if response.status_code == 429:
        return ParceleMaisRateLimitError(message, problem_details, _retry_after_ms(response))

    return ParceleMaisApiError(message, response.status_code, problem_details)


def _retry_after_ms(response: ApiResponse) -> Optional[int]:
    retry_after = response.headers.get("retry-after")
    if not retry_after:
        return None

    try:
        return int(float(retry_after) * 1000)
    except ValueError:
        pass

    try:
        retry_at = datetime.strptime(retry_after, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
        delta_ms = int((retry_at - datetime.now(timezone.utc)).total_seconds() * 1000)
        return max(0, delta_ms)
    except ValueError:
        return None
