from typing import Any

from ...webhooks.types import (
    CreateWebhookRequest,
    UpdateWebhookRequest,
    Webhook,
    WebhookAudit,
    WebHookAuthenticationType,
    WebHookType,
)


def webhook_to_public(wire: dict[str, Any]) -> Webhook:
    return Webhook(
        type=WebHookType.from_wire_value(wire["tipo"]),
        url=wire["url"],
        authentication_type=WebHookAuthenticationType.from_wire_value(wire["tipoAutenticacao"]),
    )


def webhook_audit_to_public(wire: dict[str, Any]) -> WebhookAudit:
    return WebhookAudit(
        id=wire["id"],
        type=WebHookType.from_wire_value(wire["tipo"]),
        request=wire["requisicao"],
        response=wire["resposta"],
        status_code=wire["statusCode"],
        created_at=wire["dataCriacao"],
    )


def create_webhook_request_to_wire(request: CreateWebhookRequest) -> dict[str, Any]:
    return {
        "tipo": int(request.type),
        "url": request.url,
        "tipoAutenticacao": int(request.authentication_type),
        "credencial": request.credential,
    }


def update_webhook_request_to_wire(request: UpdateWebhookRequest) -> dict[str, Any]:
    return {
        "url": request.url,
        "tipoAutenticacao": int(request.authentication_type),
        "credencial": request.credential,
    }
