from twila_parcelemais import (
    ParceleMaisApiError,
    ParceleMaisAuthenticationError,
    ParceleMaisRateLimitError,
    ParceleMaisValidationError,
)
from twila_parcelemais._internal.http.api_response import ApiResponse
from twila_parcelemais.errors.exception_factory import exception_from_response


def _response(status_code: int, body: object = None, headers: dict = None) -> ApiResponse:
    return ApiResponse(status_code=status_code, body=body, headers=headers or {})


def test_401_maps_to_authentication_error() -> None:
    error = exception_from_response(_response(401, {"detalhe": "token inválido"}))

    assert isinstance(error, ParceleMaisAuthenticationError)
    assert str(error) == "token inválido"


def test_400_with_field_errors_maps_to_validation_error() -> None:
    error = exception_from_response(_response(400, {"detalhe": "campos inválidos", "erros": {"cpf": ["obrigatório"]}}))

    assert isinstance(error, ParceleMaisValidationError)
    assert error.status_code == 400
    assert error.field_errors == {"cpf": ["obrigatório"]}


def test_400_without_field_errors_maps_to_generic_api_error() -> None:
    error = exception_from_response(_response(400, {"detalhe": "bad request"}))

    assert type(error) is ParceleMaisApiError
    assert error.status_code == 400


def test_429_maps_to_rate_limit_error_with_retry_after() -> None:
    error = exception_from_response(_response(429, {"detalhe": "muitas requisições"}, {"retry-after": "2"}))

    assert isinstance(error, ParceleMaisRateLimitError)
    assert error.retry_after_ms == 2000


def test_unmapped_status_maps_to_generic_api_error() -> None:
    error = exception_from_response(_response(500, {"detalhe": "erro interno"}))

    assert type(error) is ParceleMaisApiError
    assert error.status_code == 500


def test_error_code_reads_problem_details_type() -> None:
    error = exception_from_response(_response(404, {"tipo": "pedido-nao-encontrado", "detalhe": "não encontrado"}))

    assert error.error_code == "pedido-nao-encontrado"


def test_message_falls_back_to_generic_when_no_problem_details() -> None:
    error = exception_from_response(_response(503, None))

    assert "503" in str(error)
