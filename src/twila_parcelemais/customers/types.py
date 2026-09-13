from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Address:
    street: Optional[str] = None
    number: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    complement: Optional[str] = None


@dataclass(frozen=True)
class Customer:
    id: str
    name: str
    document: str
    date_of_birth: str
    address: Optional[Address] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None


@dataclass(frozen=True)
class ListCustomersRequest:
    name: Optional[str] = None
    document: Optional[str] = None
    page: int = 1
    page_size: int = 10
