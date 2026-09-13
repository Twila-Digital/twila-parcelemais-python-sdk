from typing import Optional

from .._internal.http.api_request_executor import ApiRequestExecutor
from .._internal.http.query_string import QueryStringBuilder
from .._internal.mapping.customer_mapper import customer_to_public
from .._internal.mapping.paged_mapper import paged_result_from_wire
from ..paged_result import PagedResult
from .types import Customer, ListCustomersRequest


class CustomersClient:
    def __init__(self, executor: ApiRequestExecutor) -> None:
        self._executor = executor

    def get(self, customer_id: str) -> Customer:
        response = self._executor.get(f"v1/customer/{customer_id}")
        ApiRequestExecutor.ensure_success(response)

        return customer_to_public(response.body)

    def list(self, request: Optional[ListCustomersRequest] = None) -> PagedResult[Customer]:
        request = request or ListCustomersRequest()

        path = (
            QueryStringBuilder()
            .add("nome", request.name)
            .add("documento", request.document)
            .add("pagina", request.page)
            .add("tamanhoPagina", request.page_size)
            .build("v1/customer/paged")
        )

        response = self._executor.get(path)
        ApiRequestExecutor.ensure_success(response)

        return paged_result_from_wire(response.body, customer_to_public)
