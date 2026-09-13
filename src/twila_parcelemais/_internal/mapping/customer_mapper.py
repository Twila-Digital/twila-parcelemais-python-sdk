from typing import Any, Optional

from ...customers.types import Address, Customer


def customer_to_public(wire: dict[str, Any]) -> Customer:
    address_wire = wire.get("endereco")
    return Customer(
        id=wire["id"],
        name=wire["nome"],
        document=wire["documento"],
        date_of_birth=wire["dataDeNascimento"],
        address=customer_address_to_public(address_wire) if address_wire else None,
        email=wire.get("email"),
        phone_number=wire.get("celular"),
    )


def customer_address_to_public(wire: dict[str, Any]) -> Optional[Address]:
    return Address(
        street=wire.get("rua"),
        number=wire.get("numero"),
        neighborhood=wire.get("bairro"),
        city=wire.get("cidade"),
        state=wire.get("estado"),
        postal_code=wire.get("cep"),
        country=wire.get("pais"),
        complement=wire.get("complemento"),
    )
