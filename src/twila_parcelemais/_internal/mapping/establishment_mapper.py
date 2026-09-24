from typing import Any

from ...establishments.types import (
    BankAccountType,
    CreateEstablishmentRequest,
    DisbursementModel,
    Establishment,
    EstablishmentAddress,
    EstablishmentBankAccount,
    EstablishmentOwner,
    UpdateEstablishmentRequest,
)


def bank_account_to_wire(bank_account: EstablishmentBankAccount) -> dict[str, Any]:
    return {
        "banco": bank_account.bank_number,
        "agencia": bank_account.agency_number,
        "digitoAgencia": bank_account.agency_digit or "",
        "conta": bank_account.account_number,
        "digitoConta": bank_account.account_digit,
        "tipoConta": int(bank_account.account_type),
        "nomeTitular": bank_account.holder_name,
        "documentoTitular": bank_account.holder_document,
    }


def address_to_wire(address: EstablishmentAddress) -> dict[str, Any]:
    return {
        "rua": address.street,
        "numero": address.number,
        "complemento": address.complement,
        "bairro": address.district,
        "cidade": address.city,
        "estado": address.state,
        "cep": address.zip_code,
        "pais": address.country,
    }


def create_establishment_request_to_wire(request: CreateEstablishmentRequest) -> dict[str, Any]:
    return {
        "documento": request.document,
        "razaoSocial": request.legal_name,
        "nomeFantasia": request.trade_name,
        "modeloDesembolso": int(request.disbursement_model),
        "responsavel": {
            "nome": request.owner.name,
            "email": request.owner.email,
            "celular": request.owner.phone,
        },
        "contaBancaria": bank_account_to_wire(request.bank_account),
        "endereco": address_to_wire(request.address) if request.address else None,
    }


def update_establishment_request_to_wire(request: UpdateEstablishmentRequest) -> dict[str, Any]:
    return {
        "nomeFantasia": request.trade_name,
        "modeloDesembolso": int(request.disbursement_model) if request.disbursement_model is not None else None,
        "endereco": address_to_wire(request.address) if request.address else None,
    }


def establishment_to_public(wire: dict[str, Any]) -> Establishment:
    bank_account = wire.get("contaBancaria")
    address = wire.get("endereco")
    disbursement_model = wire.get("modeloDesembolso")

    if disbursement_model is not None:
        disbursement_model = DisbursementModel.from_wire_value(disbursement_model)

    return Establishment(
        establishment_id=wire["estabelecimentoId"],
        document=wire["documento"],
        legal_name=wire["razaoSocial"],
        trade_name=wire["nomeFantasia"],
        is_active=wire["ativa"],
        owner=EstablishmentOwner(
            name=wire["responsavel"]["nome"],
            email=wire["responsavel"]["email"],
            phone=wire["responsavel"]["celular"],
        ),
        disbursement_model=disbursement_model,
        bank_account=EstablishmentBankAccount(
            bank_number=bank_account["banco"],
            agency_number=bank_account["agencia"],
            account_number=bank_account["conta"],
            account_digit=bank_account["digitoConta"],
            account_type=BankAccountType.from_wire_value(bank_account["tipoConta"]),
            agency_digit=bank_account.get("digitoAgencia"),
            holder_name=bank_account.get("nomeTitular"),
            holder_document=bank_account.get("documentoTitular"),
        )
        if bank_account
        else None,
        address=EstablishmentAddress(
            street=address["rua"],
            number=address["numero"],
            district=address["bairro"],
            city=address["cidade"],
            state=address["estado"],
            zip_code=address["cep"],
            complement=address.get("complemento"),
            country=address.get("pais"),
        )
        if address
        else None,
    )
