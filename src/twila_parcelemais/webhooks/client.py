from typing import Optional

from .._internal.http.api_request_executor import ApiRequestExecutor
from .._internal.http.query_string import QueryStringBuilder
from .._internal.mapping.paged_mapper import paged_result_from_wire
from .._internal.mapping.webhook_mapper import (
    create_webhook_request_to_wire,
    update_webhook_request_to_wire,
    webhook_audit_to_public,
    webhook_to_public,
)
from ..orders.types import to_iso_string
from ..paged_result import PagedResult
from .types import (
    CreateWebhookRequest,
    CreateWebhookResult,
    ListWebhookAuditRequest,
    UpdateWebhookRequest,
    Webhook,
    WebhookAudit,
    WebHookType,
)


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

    def list_audit(self, request: Optional[ListWebhookAuditRequest] = None) -> PagedResult[WebhookAudit]:
        request = request or ListWebhookAuditRequest()

        path = (
            QueryStringBuilder()
            .add("dataInicio", to_iso_string(request.start_date) if request.start_date is not None else None)
            .add("dataFim", to_iso_string(request.end_date) if request.end_date is not None else None)
            .add("pedidoId", request.order_id)
            .add("numeroPedido", request.order_number)
            .add("statusCode", request.status_code)
            .add("pagina", request.page)
            .add("tamanhoPagina", request.page_size)
            .build("v1/webhooks/auditoria")
        )

        response = self._executor.get(path)
        ApiRequestExecutor.ensure_success(response)

        return paged_result_from_wire(response.body, webhook_audit_to_public)

    def update(self, type: WebHookType, request: UpdateWebhookRequest) -> None:
        wire_request = update_webhook_request_to_wire(request)
        response = self._executor.put(f"v1/webhooks/{int(type)}", wire_request)
        ApiRequestExecutor.ensure_success(response)

    def delete(self, type: WebHookType) -> None:
        response = self._executor.delete(f"v1/webhooks/{int(type)}")
        ApiRequestExecutor.ensure_success(response)
