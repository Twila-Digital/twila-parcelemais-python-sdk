
from .._internal.http.api_request_executor import ApiRequestExecutor
from .._internal.http.query_string import QueryStringBuilder
from .._internal.mapping.simulation_mapper import installment_simulation_to_public, values_simulation_to_public
from .types import (
    CalculationValueType,
    InstallmentSimulation,
    SimulateInstallmentsRequest,
    SimulateValuesRequest,
    ValuesSimulation,
)


class SimulationsClient:
    def __init__(self, executor: ApiRequestExecutor) -> None:
        self._executor = executor

    def simulate_installments(self, request: SimulateInstallmentsRequest) -> list[InstallmentSimulation]:
        calculation_value_type = request.calculation_value_type or CalculationValueType.GROSS_AMOUNT

        path = (
            QueryStringBuilder()
            .add("valorSolicitado", request.requested_amount)
            .add("tipoValorCalculo", int(calculation_value_type))
            .build("v1/order/simulate-installments")
        )

        response = self._executor.get(path)
        ApiRequestExecutor.ensure_success(response)

        return [installment_simulation_to_public(item) for item in response.body]

    def simulate_values(self, request: SimulateValuesRequest) -> ValuesSimulation:
        calculation_value_type = request.calculation_value_type or CalculationValueType.GROSS_AMOUNT

        path = (
            QueryStringBuilder()
            .add("valor", request.amount)
            .add("prazo", request.term)
            .add("modeloJuros", 1)
            .add("tipoValorCalculo", int(calculation_value_type))
            .build("v1/order/simulate-values")
        )

        response = self._executor.get(path)
        ApiRequestExecutor.ensure_success(response)

        return values_simulation_to_public(response.body)
