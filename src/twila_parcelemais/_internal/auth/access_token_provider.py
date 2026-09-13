import threading
import time
from dataclasses import dataclass
from typing import Optional

from .token_api_client import TokenApiClient

_CLOCK_SKEW_SECONDS = 60


@dataclass
class _CachedToken:
    value: str
    expires_at_monotonic: float


class AccessTokenProvider:
    def __init__(self, token_api_client: TokenApiClient, client_id: str, client_secret: str) -> None:
        self._token_api_client = token_api_client
        self._client_id = client_id
        self._client_secret = client_secret
        self._lock = threading.Lock()
        self._cached: Optional[_CachedToken] = None

    def get_token(self) -> str:
        with self._lock:
            current = self._cached
            if current is not None and not self._is_close_to_expiry(current):
                return current.value

            response = self._token_api_client.generate(self._client_id, self._client_secret)
            fresh = _CachedToken(
                value=response["token_de_acesso"],
                expires_at_monotonic=time.monotonic() + response["expira_em_segundos"],
            )
            self._cached = fresh
            return fresh.value

    def invalidate(self) -> None:
        with self._lock:
            self._cached = None

    @staticmethod
    def _is_close_to_expiry(token: _CachedToken) -> bool:
        return time.monotonic() + _CLOCK_SKEW_SECONDS >= token.expires_at_monotonic
