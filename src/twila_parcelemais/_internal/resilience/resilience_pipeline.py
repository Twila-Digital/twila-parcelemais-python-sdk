import random
import threading
import time
from collections import deque
from typing import Callable, Optional

from ...config.resilience_options import ParceleMaisResilienceOptions
from ...errors.timeout_error import ParceleMaisTimeoutError
from ..http.api_response import ApiResponse
from .transient_failure_classifier import is_network_error, is_transient_response


class _BrokenCircuitError(Exception):
    pass


class _CircuitBreaker:
    """Sliding-window sampling breaker, equivalent to cockatiel's SamplingBreaker used in the Node SDK."""

    def __init__(self, options: ParceleMaisResilienceOptions) -> None:
        self._options = options
        self._lock = threading.Lock()
        self._events: deque[tuple[float, bool]] = deque()
        self._opened_at: Optional[float] = None
        self._half_open_trial_in_flight = False

    def before_call(self) -> None:
        with self._lock:
            if self._opened_at is None:
                return

            elapsed_ms = (time.monotonic() - self._opened_at) * 1000
            if elapsed_ms < self._options.circuit_breaker_break_duration_ms:
                raise _BrokenCircuitError()

            if self._half_open_trial_in_flight:
                raise _BrokenCircuitError()

            self._half_open_trial_in_flight = True

    def on_success(self) -> None:
        with self._lock:
            if self._opened_at is not None:
                self._opened_at = None
                self._half_open_trial_in_flight = False
                self._events.clear()
                return

            self._record(is_failure=False)

    def on_failure(self) -> None:
        with self._lock:
            if self._opened_at is not None:
                self._opened_at = time.monotonic()
                self._half_open_trial_in_flight = False
                return

            self._record(is_failure=True)
            self._maybe_open()

    def _record(self, is_failure: bool) -> None:
        now = time.monotonic()
        self._events.append((now, is_failure))
        cutoff = now - self._options.circuit_breaker_sampling_duration_ms / 1000
        while self._events and self._events[0][0] < cutoff:
            self._events.popleft()

    def _maybe_open(self) -> None:
        total = len(self._events)
        if total < self._options.circuit_breaker_minimum_throughput:
            return

        failures = sum(1 for _, failed in self._events if failed)
        if failures / total >= self._options.circuit_breaker_failure_ratio:
            self._opened_at = time.monotonic()
            self._events.clear()


class ResiliencePipeline:
    def __init__(self, options: ParceleMaisResilienceOptions) -> None:
        self._options = options
        self._circuit_breaker = _CircuitBreaker(options)

    def execute(self, retry_safe: bool, attempt: Callable[[], ApiResponse]) -> ApiResponse:
        deadline = time.monotonic() + self._options.total_timeout_ms / 1000
        max_attempts = max(1, self._options.max_retry_attempts)
        last_error: Optional[BaseException] = None

        for attempt_number in range(1, max_attempts + 1):
            if time.monotonic() >= deadline:
                raise ParceleMaisTimeoutError("A requisição excedeu o tempo limite configurado.", last_error)

            try:
                self._circuit_breaker.before_call()
            except _BrokenCircuitError as broken:
                raise ParceleMaisTimeoutError(
                    "O circuit breaker está aberto — chamadas recentes falharam de forma consistente.", broken
                ) from broken

            try:
                response = attempt()
            except BaseException as error:
                if not is_network_error(error):
                    raise

                self._circuit_breaker.on_failure()
                last_error = error

                if retry_safe and attempt_number < max_attempts and time.monotonic() < deadline:
                    time.sleep(self._backoff_seconds(attempt_number))
                    continue

                raise

            transient = is_transient_response(response, self._options)
            if transient:
                self._circuit_breaker.on_failure()
            else:
                self._circuit_breaker.on_success()

            if not transient or not retry_safe:
                return response

            if attempt_number >= max_attempts:
                return response

            remaining_seconds = deadline - time.monotonic()
            if remaining_seconds <= 0:
                return response

            delay = self._delay_seconds(attempt_number, response)
            time.sleep(min(delay, max(0.0, remaining_seconds)))

        raise AssertionError("unreachable: resilience pipeline loop did not return or raise")

    def _delay_seconds(self, attempt_number: int, response: ApiResponse) -> float:
        retry_after = _retry_after_seconds(response)
        if retry_after is not None:
            return retry_after

        return self._backoff_seconds(attempt_number)

    def _backoff_seconds(self, attempt_number: int) -> float:
        base_delay_ms = self._options.retry_base_delay_ms
        exponential: int = base_delay_ms * (2 ** max(0, attempt_number - 1))
        jitter_factor = 0.5 + random.random()
        result: float = (exponential * jitter_factor) / 1000
        return result


def _retry_after_seconds(response: ApiResponse) -> Optional[float]:
    retry_after = response.headers.get("retry-after")
    if not retry_after:
        return None

    try:
        return float(retry_after)
    except ValueError:
        return None
