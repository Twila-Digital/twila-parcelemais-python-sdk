from typing import Any

from ...simulations.types import InstallmentSimulation, ValuesSimulation


def installment_simulation_to_public(wire: dict[str, Any]) -> InstallmentSimulation:
    return InstallmentSimulation(
        total_amount=wire["valorTotalDebito"],
        term=wire["prazo"],
        installment_amount=wire["valorParcela"],
    )


def values_simulation_to_public(wire: dict[str, Any]) -> ValuesSimulation:
    establishment = wire["valoresEstabelecimento"]
    customer = wire["valoresCliente"]
    return ValuesSimulation(
        sale_amount=establishment["valorVenda"],
        disbursement_amount=establishment["valorDesembolso"],
        installment_amount=customer["valorParcela"],
    )
