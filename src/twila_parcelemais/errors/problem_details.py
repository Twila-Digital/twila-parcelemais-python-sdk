from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class ProblemDetails:
    type: Optional[str] = None
    title: Optional[str] = None
    status: Optional[int] = None
    detail: Optional[str] = None
    instance: Optional[str] = None
    errors: Optional[dict[str, Any]] = None
    correlation_id: Optional[str] = None


def parse_problem_details(body: Any) -> ProblemDetails:
    if not isinstance(body, dict):
        return ProblemDetails()

    errors = body.get("erros")

    return ProblemDetails(
        type=body.get("tipo") if isinstance(body.get("tipo"), str) else None,
        title=body.get("titulo") if isinstance(body.get("titulo"), str) else None,
        status=body.get("status") if isinstance(body.get("status"), int) else None,
        detail=body.get("detalhe") if isinstance(body.get("detalhe"), str) else None,
        instance=body.get("instancia") if isinstance(body.get("instancia"), str) else None,
        errors=errors if isinstance(errors, dict) else None,
        correlation_id=body.get("correlationId") if isinstance(body.get("correlationId"), str) else None,
    )
