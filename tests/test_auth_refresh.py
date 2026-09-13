import httpx
import respx

from twila_parcelemais import ParceleMaisClient, ParceleMaisClientOptions, ParceleMaisResilienceOptions

BASE_URL = "https://sdk-test.local/integration/"


def test_401_refreshes_token_and_retries_once(mock_router: respx.MockRouter) -> None:
    def _token_body(token: str) -> dict:
        return {"token_de_acesso": token, "expira_em_segundos": 3600, "tipo_de_token": "Bearer"}

    token_responses = iter(
        [
            httpx.Response(200, json=_token_body("stale-token")),
            httpx.Response(200, json=_token_body("fresh-token")),
        ]
    )
    mock_router.post("v1/authentication/accesstoken").mock(side_effect=lambda request: next(token_responses))

    seen_tokens = []

    def order_response(request: httpx.Request) -> httpx.Response:
        auth_header = request.headers.get("authorization", "")
        seen_tokens.append(auth_header)
        if auth_header == "Bearer stale-token":
            return httpx.Response(401, json={"detalhe": "token expirado"})
        return httpx.Response(200, json={"id": "order-1"} | _order_fields())

    mock_router.get("v1/order/order-1").mock(side_effect=order_response)

    client = ParceleMaisClient(
        ParceleMaisClientOptions(
            client_id="cid",
            client_secret="csecret",
            base_url=BASE_URL,
            resilience=ParceleMaisResilienceOptions(),
        )
    )

    order = client.orders.get("order-1")
    client.close()

    assert order.id == "order-1"
    assert seen_tokens == ["Bearer stale-token", "Bearer fresh-token"]


def _order_fields() -> dict:
    return {
        "numero": 1,
        "status": {"valor": 9, "descricao": "Comprado"},
        "documentoCliente": "12345678901",
        "razaoSocialEstabelecimento": "Loja",
        "documentoEstabelecimento": "12345678000195",
        "criadoEm": "2026-01-01T00:00:00-03:00",
    }
