import httpx
import respx

from twila_parcelemais import ListCustomersRequest, ParceleMaisClient

CUSTOMER_WIRE = {
    "id": "customer-1",
    "nome": "Maria Souza",
    "documento": "12345678901",
    "dataDeNascimento": "1990-05-20T00:00:00-03:00",
    "endereco": {"rua": "Av. Paulista", "cidade": "São Paulo", "estado": "SP"},
    "email": "maria@exemplo.com.br",
}


def test_get_maps_customer(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.get("v1/customer/customer-1").mock(return_value=httpx.Response(200, json=CUSTOMER_WIRE))

    customer = client.customers.get("customer-1")

    assert customer.id == "customer-1"
    assert customer.name == "Maria Souza"
    assert customer.address is not None
    assert customer.address.city == "São Paulo"


def test_list_maps_paged_result(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.get("v1/customer/paged").mock(
        return_value=httpx.Response(
            200,
            json={
                "itens": [CUSTOMER_WIRE],
                "pagina": {"tem_proximo": False, "tem_anterior": False, "numero": 1, "tamanho": 10, "total": 1},
            },
        )
    )

    page = client.customers.list(ListCustomersRequest())

    assert len(page.items) == 1
    assert page.items[0].id == "customer-1"
    assert page.has_next is False
