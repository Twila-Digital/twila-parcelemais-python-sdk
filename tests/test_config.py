import pytest

from twila_parcelemais import ParceleMaisConfigurationError
from twila_parcelemais.config.client_options import ParceleMaisClientOptions, resolve_client_options
from twila_parcelemais.config.environment import ParceleMaisEnvironment, environment_base_url
from twila_parcelemais.config.resilience_options import ParceleMaisResilienceOptions


def test_resolve_client_options_defaults_to_production_base_url() -> None:
    resolved = resolve_client_options(ParceleMaisClientOptions(client_id="id", client_secret="secret"))

    assert resolved.base_url == environment_base_url(ParceleMaisEnvironment.PRODUCTION)


def test_resolve_client_options_normalizes_base_url_without_trailing_slash() -> None:
    resolved = resolve_client_options(
        ParceleMaisClientOptions(client_id="id", client_secret="secret", base_url="https://example.com/integration")
    )

    assert resolved.base_url == "https://example.com/integration/"


@pytest.mark.parametrize("client_id,client_secret", [("", "secret"), ("id", ""), ("   ", "secret")])
def test_blank_credentials_raise_configuration_error(client_id: str, client_secret: str) -> None:
    with pytest.raises(ParceleMaisConfigurationError):
        resolve_client_options(ParceleMaisClientOptions(client_id=client_id, client_secret=client_secret))


def test_invalid_base_url_raises_configuration_error() -> None:
    with pytest.raises(ParceleMaisConfigurationError):
        resolve_client_options(ParceleMaisClientOptions(client_id="id", client_secret="secret", base_url="not-a-url"))


@pytest.mark.parametrize(
    "overrides",
    [
        {"max_retry_attempts": 0},
        {"total_timeout_ms": 0},
        {"attempt_timeout_ms": 0},
        {"attempt_timeout_ms": 20_000, "total_timeout_ms": 10_000},
        {"circuit_breaker_failure_ratio": 0},
        {"circuit_breaker_failure_ratio": 1.5},
        {"circuit_breaker_minimum_throughput": 1},
    ],
)
def test_invalid_resilience_options_raise_configuration_error(overrides: dict) -> None:
    with pytest.raises(ParceleMaisConfigurationError):
        resolve_client_options(
            ParceleMaisClientOptions(
                client_id="id",
                client_secret="secret",
                resilience=ParceleMaisResilienceOptions(**overrides),
            )
        )
