from collections.abc import Iterator

import httpx
import pytest
import respx

from twila_parcelemais import ParceleMaisClient, ParceleMaisClientOptions, ParceleMaisResilienceOptions

BASE_URL = "https://sdk-test.local/integration/"


@pytest.fixture
def mock_router() -> Iterator[respx.MockRouter]:
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as router:
        yield router


@pytest.fixture
def token_route(mock_router: respx.MockRouter) -> respx.Route:
    return mock_router.post("v1/authentication/accesstoken").mock(
        return_value=httpx.Response(
            200, json={"token_de_acesso": "test-token", "expira_em_segundos": 3600, "tipo_de_token": "Bearer"}
        )
    )


def make_client(token_route: respx.Route, **resilience_overrides: object) -> ParceleMaisClient:
    resilience = (
        ParceleMaisResilienceOptions(**resilience_overrides) if resilience_overrides else ParceleMaisResilienceOptions()
    )

    options = ParceleMaisClientOptions(
        client_id="test-client-id",
        client_secret="test-client-secret",
        base_url=BASE_URL,
        resilience=resilience,
    )
    return ParceleMaisClient(options)


@pytest.fixture
def client(token_route: respx.Route) -> Iterator[ParceleMaisClient]:
    c = make_client(token_route)
    yield c
    c.close()
