from typing import Any

from ...orders.types import Address, CreateOrderRequest, Order, OrderStatus, to_iso_string


def order_to_public(wire: dict[str, Any]) -> Order:
    status = wire["status"]
    return Order(
        id=wire["id"],
        number=wire["numero"],
        status=OrderStatus.from_wire_value(status["valor"]),
        status_description=status["descricao"],
        customer_document=wire["documentoCliente"],
        establishment_legal_name=wire["razaoSocialEstabelecimento"],
        establishment_document=wire["documentoEstabelecimento"],
        created_at=wire["criadoEm"],
        total=wire.get("total"),
        customer_name=wire.get("nomeCliente"),
        term=wire.get("prazo"),
        description=wire.get("descricao"),
        approved_amount=wire.get("valorAprovado"),
        disbursed=wire.get("desembolsado"),
        disbursed_at=wire.get("desembolsadoEm"),
        requested_amount=wire.get("valorSolicitado"),
    )


def address_to_wire(address: Address) -> dict[str, Any]:
    return {
        "logradouro": address.street,
        "numero": address.number,
        "bairro": address.neighborhood,
        "cidade": address.city,
        "estado": address.state,
        "cep": address.postal_code,
        "complemento": address.complement,
    }


def create_order_request_to_wire(request: CreateOrderRequest) -> dict[str, Any]:
    return {
        "cpf": request.cpf,
        "celular": request.phone_number,
        "documentoEstabelecimento": request.establishment_document,
        "valorSolicitado": request.requested_amount,
        "nome": request.name,
        "email": request.email,
        "dataDeNascimento": to_iso_string(request.date_of_birth),
        "endereco": address_to_wire(request.address),
    }
