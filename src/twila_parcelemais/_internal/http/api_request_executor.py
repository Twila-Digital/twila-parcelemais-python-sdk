import uuid
from typing import Any, Optional
from urllib.parse import urljoin

import httpx

from ...config.resilience_options import ParceleMaisResilienceOptions
from ...errors.exception_factory import exception_from_response
from ..auth.access_token_provider import AccessTokenProvider
from ..idempotency.idempotency_classifier import is_retry_safe, requires_idempotency_key
from ..resilience.resilience_pipeline import ResiliencePipeline
from .api_response import ApiResponse


class ApiRequestExecutor:
    def __init__(
        self,
        base_url: str,
        token_provider: AccessTokenProvider,
        resilience_options: ParceleMaisResilienceOptions,
    ) -> None:
        self._base_url = base_url
        self._token_provider = token_provider
        self._resilience_options = resilience_options
        self._http = httpx.Client()
        self._resilience = ResiliencePipeline(resilience_options)

    def close(self) -> None:
        self._http.close()

    def get(self, path: str) -> ApiResponse:
        return self._send("GET", path, None, self._resilience_options.attempt_timeout_ms)

    def post(self, path: str, body: Any, attempt_timeout_ms: Optional[int] = None) -> ApiResponse:
        return self._send("POST", path, body, attempt_timeout_ms or self._resilience_options.attempt_timeout_ms)

    def put(self, path: str, body: Any) -> ApiResponse:
        return self._send("PUT", path, body, self._resilience_options.attempt_timeout_ms)

    def delete(self, path: str) -> ApiResponse:
        return self._send("DELETE", path, None, self._resilience_options.attempt_timeout_ms)

    @staticmethod
    def ensure_success(response: ApiResponse) -> None:
        if not (200 <= response.status_code < 300):
            raise exception_from_response(response)

    def _send(self, method: str, path: str, body: Any, attempt_timeout_ms: int) -> ApiResponse:
        idempotency_key = (
            uuid.uuid4().hex
            if not self._resilience_options.disable_automatic_idempotency_key and requires_idempotency_key(method, path)
            else None
        )

        retry_safe = is_retry_safe(method, path, idempotency_key is not None)

        return self._resilience.execute(
            retry_safe, lambda: self._send_with_auth(method, path, body, idempotency_key, attempt_timeout_ms)
        )

    def _send_with_auth(
        self,
        method: str,
        path: str,
        body: Any,
        idempotency_key: Optional[str],
        attempt_timeout_ms: int,
    ) -> ApiResponse:
        token = self._token_provider.get_token()
        response = self._send_once(method, path, body, idempotency_key, attempt_timeout_ms, token)

        if response.status_code != 401:
            return response

        self._token_provider.invalidate()
        new_token = self._token_provider.get_token()
        retried = self._send_once(method, path, body, idempotency_key, attempt_timeout_ms, new_token)

        if retried.status_code != 401:
            return retried

        raise exception_from_response(retried)

    def _send_once(
        self,
        method: str,
        path: str,
        body: Any,
        idempotency_key: Optional[str],
        attempt_timeout_ms: int,
        token: str,
    ) -> ApiResponse:
        url = urljoin(self._base_url, path)

        headers = {"Authorization": f"Bearer {token}"}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        raw = self._http.request(method, url, json=body, headers=headers, timeout=attempt_timeout_ms / 1000)

        return ApiResponse(status_code=raw.status_code, body=_safe_json(raw), headers=dict(raw.headers))


def _safe_json(raw: httpx.Response) -> Any:
    if not raw.content:
        return None
    try:
        return raw.json()
    except ValueError:
        return None
