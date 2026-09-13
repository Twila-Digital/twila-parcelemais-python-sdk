import httpx
import pytest

from twila_parcelemais import ParceleMaisResilienceOptions, ParceleMaisTimeoutError
from twila_parcelemais._internal.http.api_response import ApiResponse
from twila_parcelemais._internal.resilience.resilience_pipeline import ResiliencePipeline

FAST_OPTIONS = ParceleMaisResilienceOptions(
    total_timeout_ms=5_000,
    attempt_timeout_ms=1_000,
    max_retry_attempts=3,
    retry_base_delay_ms=1,
)


def _response(status_code: int) -> ApiResponse:
    return ApiResponse(status_code=status_code, body={}, headers={})


def test_successful_response_does_not_retry() -> None:
    pipeline = ResiliencePipeline(FAST_OPTIONS)
    calls = {"count": 0}

    def attempt() -> ApiResponse:
        calls["count"] += 1
        return _response(200)

    result = pipeline.execute(True, attempt)

    assert result.status_code == 200
    assert calls["count"] == 1


def test_transient_response_retries_when_retry_safe() -> None:
    pipeline = ResiliencePipeline(FAST_OPTIONS)
    calls = {"count": 0}

    def attempt() -> ApiResponse:
        calls["count"] += 1
        return _response(503) if calls["count"] < 3 else _response(200)

    result = pipeline.execute(True, attempt)

    assert result.status_code == 200
    assert calls["count"] == 3


def test_transient_response_does_not_retry_when_not_retry_safe() -> None:
    pipeline = ResiliencePipeline(FAST_OPTIONS)
    calls = {"count": 0}

    def attempt() -> ApiResponse:
        calls["count"] += 1
        return _response(503)

    result = pipeline.execute(False, attempt)

    assert result.status_code == 503
    assert calls["count"] == 1


def test_network_error_retries_and_eventually_raises() -> None:
    pipeline = ResiliencePipeline(FAST_OPTIONS)
    calls = {"count": 0}

    def attempt() -> ApiResponse:
        calls["count"] += 1
        raise httpx.ConnectError("boom")

    with pytest.raises(httpx.ConnectError):
        pipeline.execute(True, attempt)

    assert calls["count"] == FAST_OPTIONS.max_retry_attempts


def test_total_timeout_raises_timeout_error() -> None:
    options = ParceleMaisResilienceOptions(
        total_timeout_ms=1,
        attempt_timeout_ms=1_000,
        max_retry_attempts=5,
        retry_base_delay_ms=50,
    )
    pipeline = ResiliencePipeline(options)

    def attempt() -> ApiResponse:
        return _response(503)

    with pytest.raises(ParceleMaisTimeoutError):
        pipeline.execute(True, attempt)


def test_circuit_breaker_opens_after_failure_threshold_and_blocks_next_call() -> None:
    options = ParceleMaisResilienceOptions(
        total_timeout_ms=5_000,
        attempt_timeout_ms=1_000,
        max_retry_attempts=1,
        circuit_breaker_minimum_throughput=2,
        circuit_breaker_failure_ratio=0.5,
        circuit_breaker_break_duration_ms=60_000,
    )
    pipeline = ResiliencePipeline(options)

    def failing_attempt() -> ApiResponse:
        return _response(503)

    for _ in range(2):
        pipeline.execute(False, failing_attempt)

    def healthy_attempt() -> ApiResponse:
        return _response(200)

    with pytest.raises(ParceleMaisTimeoutError):
        pipeline.execute(False, healthy_attempt)
