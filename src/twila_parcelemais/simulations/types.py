from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class CalculationValueType(IntEnum):
    GROSS_AMOUNT = 1
    LIQUID_AMOUNT = 2
    UNKNOWN = -1

    @classmethod
    def from_wire_value(cls, value: int) -> "CalculationValueType":
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


@dataclass(frozen=True)
class SimulateInstallmentsRequest:
    requested_amount: float
    calculation_value_type: Optional[CalculationValueType] = None


@dataclass(frozen=True)
class SimulateValuesRequest:
    amount: float
    term: int
    calculation_value_type: Optional[CalculationValueType] = None


@dataclass(frozen=True)
class InstallmentSimulation:
    total_amount: float
    term: int
    installment_amount: float


@dataclass(frozen=True)
class ValuesSimulation:
    sale_amount: float
    disbursement_amount: float
    installment_amount: float
