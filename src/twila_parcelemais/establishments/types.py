from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class DisbursementModel(IntEnum):
    ESTABLISHMENT_CHAIN = 1
    ESTABLISHMENT = 2
    EXTERNAL = 3
    UNKNOWN = -1

    @classmethod
    def from_wire_value(cls, value: int) -> "DisbursementModel":
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN

class BankAccountType(IntEnum):
    CURRENT = 1
    SAVINGS = 2
    PAYMENT = 3
    UNKNOWN = -1

    @classmethod
    def from_wire_value(cls, value: int) -> "BankAccountType":
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN

@dataclass(frozen=True)
class EstablishmentOwner:
    name: str
    email: str
    phone: str

@dataclass(frozen=True)
class EstablishmentBankAccount:
    bank_number: str
    agency_number: str
    account_number: str
    account_digit: str
    account_type: BankAccountType
    agency_digit: Optional[str] = None
    holder_name: Optional[str] = None
    holder_document: Optional[str] = None

@dataclass(frozen=True)
class EstablishmentAddress:
    street: str
    number: str
    district: str
    city: str
    state: str
    zip_code: str
    complement: Optional[str] = None
    country: Optional[str] = None

@dataclass(frozen=True)
class Establishment:
    establishment_id: str
    document: str
    legal_name: str
    trade_name: str
    is_active: bool
    owner: EstablishmentOwner
    disbursement_model: Optional[DisbursementModel] = None
    bank_account: Optional[EstablishmentBankAccount] = None
    address: Optional[EstablishmentAddress] = None

@dataclass(frozen=True)
class CreateEstablishmentRequest:
    document: str
    legal_name: str
    trade_name: str
    disbursement_model: DisbursementModel
    owner: EstablishmentOwner
    bank_account: EstablishmentBankAccount
    address: EstablishmentAddress

@dataclass(frozen=True)
class CreateEstablishmentResult:
    establishment_id: str

@dataclass(frozen=True)
class UpdateEstablishmentRequest:
    trade_name: str
    disbursement_model: Optional[DisbursementModel] = None
    address: Optional[EstablishmentAddress] = None

@dataclass(frozen=True)
class ListEstablishmentsRequest:
    trade_name: Optional[str] = None
    is_active: Optional[bool] = None
