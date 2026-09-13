from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from ..errors.configuration_error import ParceleMaisConfigurationError
from .environment import ParceleMaisEnvironment, environment_base_url
from .resilience_options import DEFAULT_RESILIENCE_OPTIONS, ParceleMaisResilienceOptions


@dataclass(frozen=True)
class ParceleMaisClientOptions:
    client_id: str
    client_secret: str
    environment: ParceleMaisEnvironment = ParceleMaisEnvironment.PRODUCTION
    base_url: Optional[str] = None
    resilience: ParceleMaisResilienceOptions = DEFAULT_RESILIENCE_OPTIONS


@dataclass(frozen=True)
class ResolvedParceleMaisClientOptions:
    client_id: str
    client_secret: str
    base_url: str
    resilience: ParceleMaisResilienceOptions


def resolve_client_options(options: ParceleMaisClientOptions) -> ResolvedParceleMaisClientOptions:
    _validate(options)

    base_url = _resolve_base_url(options)

    return ResolvedParceleMaisClientOptions(
        client_id=options.client_id,
        client_secret=options.client_secret,
        base_url=base_url,
        resilience=options.resilience,
    )


def _resolve_base_url(options: ParceleMaisClientOptions) -> str:
    raw = options.base_url or environment_base_url(options.environment)
    return raw if raw.endswith("/") else f"{raw}/"


def _validate(options: ParceleMaisClientOptions) -> None:
    if _is_blank(options.client_id):
        raise ParceleMaisConfigurationError("client_id é obrigatório.")
    if _is_blank(options.client_secret):
        raise ParceleMaisConfigurationError("client_secret é obrigatório.")

    if options.base_url is not None:
        parsed = urlparse(options.base_url)
        if not parsed.scheme or not parsed.netloc:
            raise ParceleMaisConfigurationError("base_url, quando informada, deve ser uma URL absoluta válida.")

    resilience = options.resilience

    if resilience.max_retry_attempts < 1:
        raise ParceleMaisConfigurationError("resilience.max_retry_attempts deve ser maior ou igual a 1.")

    if resilience.total_timeout_ms <= 0:
        raise ParceleMaisConfigurationError("resilience.total_timeout_ms deve ser maior que zero.")

    if resilience.attempt_timeout_ms <= 0:
        raise ParceleMaisConfigurationError("resilience.attempt_timeout_ms deve ser maior que zero.")

    if resilience.attempt_timeout_ms > resilience.total_timeout_ms:
        raise ParceleMaisConfigurationError(
            "resilience.attempt_timeout_ms não pode ser maior que resilience.total_timeout_ms."
        )

    if not (0 < resilience.circuit_breaker_failure_ratio <= 1):
        raise ParceleMaisConfigurationError(
            "resilience.circuit_breaker_failure_ratio deve estar entre 0 (exclusivo) e 1 (inclusivo)."
        )

    if resilience.circuit_breaker_minimum_throughput < 2:
        raise ParceleMaisConfigurationError(
            "resilience.circuit_breaker_minimum_throughput deve ser maior ou igual a 2."
        )


def _is_blank(value: Optional[str]) -> bool:
    return value is None or value.strip() == ""
