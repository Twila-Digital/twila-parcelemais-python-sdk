from typing import Optional

from .._internal.http.api_request_executor import ApiRequestExecutor
from .._internal.http.query_string import QueryStringBuilder
from .._internal.mapping.order_mapper import create_order_request_to_wire, order_to_public
from .._internal.mapping.paged_mapper import paged_result_from_wire
from ..paged_result import PagedResult
from .types import CheckoutLink, CreateOrderRequest, InvoiceFile, ListOrdersRequest, Order, to_iso_string


class OrdersClient:
    def __init__(self, executor: ApiRequestExecutor, invoice_upload_attempt_timeout_ms: int) -> None:
        self._executor = executor
        self._invoice_upload_attempt_timeout_ms = invoice_upload_attempt_timeout_ms

    def create(self, request: CreateOrderRequest) -> str:
        wire_request = create_order_request_to_wire(request)
        response = self._executor.post("v1/order", wire_request)
        ApiRequestExecutor.ensure_success(response)

        return str(response.body["pedidoId"])

    def get(self, order_id: str) -> Order:
        response = self._executor.get(f"v1/order/{order_id}")
        ApiRequestExecutor.ensure_success(response)

        return order_to_public(response.body)

    def list(self, request: Optional[ListOrdersRequest] = None) -> PagedResult[Order]:
        request = request or ListOrdersRequest()

        path = (
            QueryStringBuilder()
            .add("status", int(request.status) if request.status is not None else None)
            .add("documentoCliente", request.customer_document)
            .add("dataInicio", to_iso_string(request.start_date) if request.start_date is not None else None)
            .add("dataFim", to_iso_string(request.end_date) if request.end_date is not None else None)
            .add("numero", request.number)
            .add("documentoLoja", request.establishment_document)
            .add("descricao", request.description)
            .add("pagina", request.page)
            .add("tamanhoPagina", request.page_size)
            .build("v1/order/paged")
        )

        response = self._executor.get(path)
        ApiRequestExecutor.ensure_success(response)

        return paged_result_from_wire(response.body, order_to_public)

    def start_cdc_sale(self, order_id: str) -> CheckoutLink:
        response = self._executor.post("v1/order/start-cdc-sale", {"pedidoId": order_id})
        ApiRequestExecutor.ensure_success(response)

        return CheckoutLink(url=response.body.get("linkPagamento"))

    def import_invoice(self, order_id: str, file: InvoiceFile) -> None:
        wire_request = {"pedidoId": order_id, "arquivoBase64": file.base64_content, "nomeArquivo": file.file_name}
        response = self._executor.post("v1/order/invoice", wire_request, self._invoice_upload_attempt_timeout_ms)
        ApiRequestExecutor.ensure_success(response)
