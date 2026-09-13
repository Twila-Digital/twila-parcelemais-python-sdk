import base64
from dataclasses import dataclass
from datetime import date, datetime
from enum import IntEnum
from typing import Optional, Union


class OrderStatus(IntEnum):
    UNDEFINED = 0
    ANALYSING = 1
    APPROVED = 2
    UNAVAILABLE_BALANCE = 3
    ANALYSIS_EXPIRED = 4
    PENDING_PAYMENT = 5
    BIOMETRY_REFUSED = 6
    BIOMETRY_APPROVED = 7
    PAYMENT_REFUSED = 8
    PURCHASED = 9
    UNAUTHORIZED = 10
    PENDING_AUTHORIZATION = 11
    AWAITING_REGISTRATION = 12
    SALE_NOT_STARTED = 13
    CANCELED = 14
    BILLING = 15
    COMPLETED = 16
    FROZEN = 17
    PENDING_PAYMENT_CONFIRMATION = 18
    DISBURSED = 19
    UNKNOWN = -1

    @classmethod
    def from_wire_value(cls, value: int) -> "OrderStatus":
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


DateLike = Union[str, date, datetime]


@dataclass(frozen=True)
class Address:
    street: str
    number: str
    neighborhood: str
    city: str
    state: str
    postal_code: str
    complement: Optional[str] = None


@dataclass(frozen=True)
class CreateOrderRequest:
    cpf: str
    phone_number: str
    establishment_document: str
    requested_amount: float
    name: str
    email: str
    date_of_birth: DateLike
    address: Address


@dataclass(frozen=True)
class Order:
    id: str
    number: int
    status: OrderStatus
    status_description: str
    customer_document: str
    establishment_legal_name: str
    establishment_document: str
    created_at: str
    total: Optional[float] = None
    customer_name: Optional[str] = None
    term: Optional[int] = None
    description: Optional[str] = None
    approved_amount: Optional[float] = None
    disbursed: Optional[bool] = None
    disbursed_at: Optional[str] = None
    requested_amount: Optional[float] = None


@dataclass(frozen=True)
class ListOrdersRequest:
    status: Optional[OrderStatus] = None
    customer_document: Optional[str] = None
    start_date: Optional[DateLike] = None
    end_date: Optional[DateLike] = None
    number: Optional[int] = None
    establishment_document: Optional[str] = None
    description: Optional[str] = None
    page: int = 1
    page_size: int = 10


@dataclass(frozen=True)
class CheckoutLink:
    url: Optional[str] = None


@dataclass(frozen=True)
class InvoiceFile:
    file_name: str
    base64_content: str

    @classmethod
    def from_bytes(cls, content: bytes, file_name: str) -> "InvoiceFile":
        return cls(file_name=file_name, base64_content=base64.b64encode(content).decode("ascii"))


def to_iso_string(value: DateLike) -> str:
    return value if isinstance(value, str) else value.isoformat()
