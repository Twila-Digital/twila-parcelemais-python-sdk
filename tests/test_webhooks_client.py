from datetime import datetime, timezone

import httpx
import respx

from twila_parcelemais import (
    CreateWebhookRequest,
    ListWebhookAuditRequest,
    ParceleMaisClient,
    UpdateWebhookRequest,
    WebHookAuthenticationType,
    WebHookType,
)


def test_create_returns_signing_secret(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.post("v1/webhooks").mock(return_value=httpx.Response(200, json={"chaveAssinatura": "whsec_abc"}))

    result = client.webhooks.create(
        CreateWebhookRequest(
            type=WebHookType.ORDER,
            url="https://example.com/webhook",
            authentication_type=WebHookAuthenticationType.NONE,
        )
    )

    assert result.signing_secret == "whsec_abc"


def test_list_maps_webhooks(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.get("v1/webhooks").mock(
        return_value=httpx.Response(
            200, json=[{"tipo": 3, "url": "https://example.com/webhook", "tipoAutenticacao": 1}]
        )
    )

    webhooks = client.webhooks.list()

    assert len(webhooks) == 1
    assert webhooks[0].type is WebHookType.ORDER
    assert webhooks[0].authentication_type is WebHookAuthenticationType.NONE


AUDIT_WIRE = {
    "id": "audit-1",
    "tipo": 3,
    "requisicao": '{"pedidoId":"order-1"}',
    "resposta": "OK",
    "statusCode": 200,
    "dataCriacao": "2026-09-20T10:00:00Z",
}


def test_list_audit_maps_paged_result(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.get("v1/webhooks/auditoria").mock(
        return_value=httpx.Response(
            200,
            json={
                "itens": [AUDIT_WIRE],
                "pagina": {"tem_proximo": True, "tem_anterior": False, "numero": 1, "tamanho": 10, "total": 25},
            },
        )
    )

    page = client.webhooks.list_audit(ListWebhookAuditRequest(page=1, page_size=10))

    assert len(page.items) == 1
    audit = page.items[0]
    assert audit.id == "audit-1"
    assert audit.type is WebHookType.ORDER
    assert audit.request == '{"pedidoId":"order-1"}'
    assert audit.response == "OK"
    assert audit.status_code == 200
    assert audit.created_at == "2026-09-20T10:00:00Z"
    assert page.has_next is True
    assert page.total_count == 25


def test_list_audit_without_request_sends_only_default_paging(
    mock_router: respx.MockRouter, client: ParceleMaisClient
) -> None:
    route = mock_router.get("v1/webhooks/auditoria").mock(
        return_value=httpx.Response(
            200,
            json={
                "itens": [],
                "pagina": {"tem_proximo": False, "tem_anterior": False, "numero": 1, "tamanho": 10, "total": 0},
            },
        )
    )

    page = client.webhooks.list_audit()

    assert page.items == []
    assert dict(route.calls.last.request.url.params) == {"pagina": "1", "tamanhoPagina": "10"}


def test_list_audit_sends_filters_as_query(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    route = mock_router.get("v1/webhooks/auditoria").mock(
        return_value=httpx.Response(
            200,
            json={
                "itens": [],
                "pagina": {"tem_proximo": False, "tem_anterior": True, "numero": 2, "tamanho": 5, "total": 5},
            },
        )
    )

    client.webhooks.list_audit(
        ListWebhookAuditRequest(
            start_date=datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc),
            end_date="2026-09-30T23:59:59Z",
            order_id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
            order_number=42,
            status_code=500,
            page=2,
            page_size=5,
        )
    )

    assert dict(route.calls.last.request.url.params) == {
        "dataInicio": "2026-09-01T00:00:00+00:00",
        "dataFim": "2026-09-30T23:59:59Z",
        "pedidoId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "numeroPedido": "42",
        "statusCode": "500",
        "pagina": "2",
        "tamanhoPagina": "5",
    }
    # '+' do offset precisa ir como %2B; cru, o servidor o leria como espaço.
    assert "dataInicio=2026-09-01T00%3A00%3A00%2B00%3A00" in str(route.calls.last.request.url)


def test_update_sends_put(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    route = mock_router.put("v1/webhooks/3").mock(return_value=httpx.Response(204))

    client.webhooks.update(
        WebHookType.ORDER,
        UpdateWebhookRequest(url="https://example.com/new", authentication_type=WebHookAuthenticationType.NONE),
    )

    assert route.called


def test_delete_sends_delete(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    route = mock_router.delete("v1/webhooks/3").mock(return_value=httpx.Response(204))

    client.webhooks.delete(WebHookType.ORDER)

    assert route.called
