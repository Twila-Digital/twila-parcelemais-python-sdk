
from .._internal.http.api_request_executor import ApiRequestExecutor
from .._internal.mapping.webhook_mapper import (
    create_webhook_request_to_wire,
    update_webhook_request_to_wire,
    webhook_to_public,
)
from .types import CreateWebhookRequest, CreateWebhookResult, UpdateWebhookRequest, Webhook, WebHookType


class WebhooksClient:
    def __init__(self, executor: ApiRequestExecutor) -> None:
        self._executor = executor

    def create(self, request: CreateWebhookRequest) -> CreateWebhookResult:
        wire_request = create_webhook_request_to_wire(request)
        response = self._executor.post("v1/webhooks", wire_request)
        ApiRequestExecutor.ensure_success(response)

        return CreateWebhookResult(signing_secret=response.body["chaveAssinatura"])

    def list(self) -> list[Webhook]:
        response = self._executor.get("v1/webhooks")
        ApiRequestExecutor.ensure_success(response)

        return [webhook_to_public(item) for item in response.body]

    def update(self, type: WebHookType, request: UpdateWebhookRequest) -> None:
        wire_request = update_webhook_request_to_wire(request)
        response = self._executor.put(f"v1/webhooks/{int(type)}", wire_request)
        ApiRequestExecutor.ensure_success(response)

    def delete(self, type: WebHookType) -> None:
        response = self._executor.delete(f"v1/webhooks/{int(type)}")
        ApiRequestExecutor.ensure_success(response)
