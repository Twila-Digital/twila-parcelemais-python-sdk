import httpx
import respx

from twila_parcelemais import (
    CreateWebhookRequest,
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
