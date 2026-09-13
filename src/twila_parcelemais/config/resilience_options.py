from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ParceleMaisResilienceOptions:
    total_timeout_ms: int = 30_000
    attempt_timeout_ms: int = 10_000
    invoice_upload_attempt_timeout_ms: int = 60_000
    max_retry_attempts: int = 3
    retry_base_delay_ms: int = 500
    circuit_breaker_failure_ratio: float = 0.5
    circuit_breaker_sampling_duration_ms: int = 30_000
    circuit_breaker_minimum_throughput: int = 10
    circuit_breaker_break_duration_ms: int = 15_000
    retry_on_500: bool = False
    disable_automatic_idempotency_key: bool = False


DEFAULT_RESILIENCE_OPTIONS = ParceleMaisResilienceOptions()


def resolve_resilience_options(
    overrides: Optional["ParceleMaisResilienceOptions"] = None,
) -> ParceleMaisResilienceOptions:
    if overrides is None:
        return DEFAULT_RESILIENCE_OPTIONS
    return overrides
