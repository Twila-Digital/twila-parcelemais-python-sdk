from typing import Any

import httpx

from ...errors.authentication_error import ParceleMaisAuthenticationError
from ...errors.exception_factory import exception_from_response
from ..http.api_response import ApiResponse


class TokenApiClient:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self._http = httpx.Client(base_url=base_url, timeout=timeout_seconds)

    def close(self) -> None:
        self._http.close()

    def generate(self, client_id: str, client_secret: str) -> dict[str, Any]:
        body = {"clientId": client_id, "clientSecret": client_secret}

        try:
            raw = self._http.post("v1/authentication/accesstoken", json=body)
        except httpx.HTTPError as error:
            raise ParceleMaisAuthenticationError("Falha de rede ao gerar o token de acesso.", error) from error

        response = ApiResponse(status_code=raw.status_code, body=_safe_json(raw), headers=dict(raw.headers))

        if not (200 <= response.status_code < 300):
            raise exception_from_response(response)

        result = response.body
        if not isinstance(result, dict) or not result.get("token_de_acesso"):
            raise ParceleMaisAuthenticationError(
                "A API do Parcele+ retornou uma resposta vazia ao gerar o token de acesso."
            )

        return result


def _safe_json(raw: httpx.Response) -> Any:
    if not raw.content:
        return None
    try:
        return raw.json()
    except ValueError:
        return None
