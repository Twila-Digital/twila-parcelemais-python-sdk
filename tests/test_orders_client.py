import httpx
import respx

from twila_parcelemais import (
    CreateOrderRequest,
    ListOrdersRequest,
    OrderAddress,
    OrderStatus,
    ParceleMaisClient,
)

ORDER_WIRE = {
    "id": "order-1",
    "numero": 42,
    "status": {"valor": 9, "descricao": "Comprado"},
    "documentoCliente": "12345678901",
    "razaoSocialEstabelecimento": "Loja Exemplo",
    "documentoEstabelecimento": "12345678000195",
    "criadoEm": "2026-01-01T00:00:00-03:00",
}


def _address() -> OrderAddress:
    return OrderAddress(
        street="Av. Paulista",
        number="1578",
        neighborhood="Bela Vista",
        city="São Paulo",
        state="SP",
        postal_code="01311000",
    )


def test_create_returns_order_id(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.post("v1/order").mock(return_value=httpx.Response(200, json={"pedidoId": "order-1"}))

    order_id = client.orders.create(
        CreateOrderRequest(
            cpf="12345678901",
            phone_number="+5511999998888",
            establishment_document="12345678000195",
            requested_amount=1500.0,
            name="Maria Souza",
            email="maria@exemplo.com.br",
            date_of_birth="1990-05-20T00:00:00-03:00",
            address=_address(),
        )
    )

    assert order_id == "order-1"


def test_get_maps_status_and_fields(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.get("v1/order/order-1").mock(return_value=httpx.Response(200, json=ORDER_WIRE))

    order = client.orders.get("order-1")

    assert order.id == "order-1"
    assert order.number == 42
    assert order.status is OrderStatus.PURCHASED
    assert order.status_description == "Comprado"
    assert order.customer_document == "12345678901"


def test_list_maps_paged_result(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.get("v1/order/paged").mock(
        return_value=httpx.Response(
            200,
            json={
                "itens": [ORDER_WIRE],
                "pagina": {"tem_proximo": True, "tem_anterior": False, "numero": 1, "tamanho": 10, "total": 25},
            },
        )
    )

    page = client.orders.list(ListOrdersRequest(page=1, page_size=10))

    assert len(page.items) == 1
    assert page.items[0].id == "order-1"
    assert page.has_next is True
    assert page.total_count == 25


def test_start_cdc_sale_returns_checkout_link(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.post("v1/order/start-cdc-sale").mock(
        return_value=httpx.Response(200, json={"linkPagamento": "https://pay.example.com/abc"})
    )

    link = client.orders.start_cdc_sale("order-1")

    assert link.url == "https://pay.example.com/abc"
