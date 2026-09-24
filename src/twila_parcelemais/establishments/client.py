from typing import Optional

from .._internal.http.api_request_executor import ApiRequestExecutor
from .._internal.http.query_string import QueryStringBuilder
from .._internal.mapping.establishment_mapper import (
    bank_account_to_wire,
    create_establishment_request_to_wire,
    establishment_to_public,
    update_establishment_request_to_wire,
)
from .types import (
    CreateEstablishmentRequest,
    CreateEstablishmentResult,
    Establishment,
    EstablishmentBankAccount,
    ListEstablishmentsRequest,
    UpdateEstablishmentRequest,
)


class EstablishmentsClient:
    def __init__(self, executor: ApiRequestExecutor) -> None:
        self._executor = executor

    def create(self, request: CreateEstablishmentRequest) -> CreateEstablishmentResult:
        wire_request = create_establishment_request_to_wire(request)
        response = self._executor.post("v1/establishment", wire_request)
        ApiRequestExecutor.ensure_success(response)

        return CreateEstablishmentResult(establishment_id=response.body["estabelecimentoId"])

    def get(self, establishment_id: str) -> Establishment:
        response = self._executor.get(f"v1/establishment/{establishment_id}")
        ApiRequestExecutor.ensure_success(response)

        return establishment_to_public(response.body)

    def list(self, request: Optional[ListEstablishmentsRequest] = None) -> list[Establishment]:
        request = request or ListEstablishmentsRequest()

        path = (
            QueryStringBuilder()
            .add("nomeFantasia", request.trade_name)
            .add("ativa", None if request.is_active is None else str(request.is_active).lower())
            .build("v1/establishment/list")
        )

        response = self._executor.get(path)
        ApiRequestExecutor.ensure_success(response)

        return [establishment_to_public(item) for item in response.body]

    def update(self, establishment_id: str, request: UpdateEstablishmentRequest) -> None:
        wire_request = update_establishment_request_to_wire(request)
        response = self._executor.put(f"v1/establishment/{establishment_id}", wire_request)
        ApiRequestExecutor.ensure_success(response)

    def update_bank_account(self, establishment_id: str, bank_account: EstablishmentBankAccount) -> None:
        response = self._executor.put(
            f"v1/establishment/{establishment_id}/bank-account", bank_account_to_wire(bank_account)
        )
        ApiRequestExecutor.ensure_success(response)

    def activate(self, establishment_id: str) -> None:
        self._set_active(establishment_id, True)

    def deactivate(self, establishment_id: str) -> None:
        self._set_active(establishment_id, False)

    def _set_active(self, establishment_id: str, is_active: bool) -> None:
        response = self._executor.put(f"v1/establishment/{establishment_id}/status", {"ativa": is_active})
        ApiRequestExecutor.ensure_success(response)
