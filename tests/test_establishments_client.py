import json

import httpx
import pytest
import respx

from twila_parcelemais import (
    BankAccountType,
    CreateEstablishmentRequest,
    DisbursementModel,
    EstablishmentAddress,
    EstablishmentBankAccount,
    EstablishmentOwner,
    ListEstablishmentsRequest,
    ParceleMaisApiError,
    ParceleMaisClient,
    UpdateEstablishmentRequest,
)

ESTABLISHMENT_ID = "establishment-1"

ESTABLISHMENT_WIRE = {
    "estabelecimentoId": ESTABLISHMENT_ID,
    "documento": "12345678000199",
    "razaoSocial": "Loja Centro LTDA",
    "nomeFantasia": "Loja Centro",
    "ativa": True,
    "modeloDesembolso": 1,
    "responsavel": {"nome": "Maria Souza", "email": "maria@loja.com.br", "celular": "+5511999998888"},
    "contaBancaria": {
        "banco": "341",
        "agencia": "1234",
        "digitoAgencia": "",
        "conta": "56789",
        "digitoConta": "0",
        "tipoConta": 1,
        "nomeTitular": None,
        "documentoTitular": None,
    },
    "endereco": {
        "rua": "Rua Exemplo",
        "numero": "100",
        "complemento": None,
        "bairro": "Centro",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01310100",
        "pais": "Brasil",
    },
}


def new_create_request() -> CreateEstablishmentRequest:
    return CreateEstablishmentRequest(
        document="12345678000199",
        legal_name="Loja Centro LTDA",
        trade_name="Loja Centro",
        disbursement_model=DisbursementModel.ESTABLISHMENT_CHAIN,
        owner=EstablishmentOwner(name="Maria Souza", email="maria@loja.com.br", phone="+5511999998888"),
        bank_account=EstablishmentBankAccount(
            bank_number="341",
            agency_number="1234",
            account_number="56789",
            account_digit="0",
            account_type=BankAccountType.CURRENT,
        ),
        address=EstablishmentAddress(
            street="Rua Exemplo",
            number="100",
            district="Centro",
            city="São Paulo",
            state="SP",
            zip_code="01310100",
        ),
    )


def test_create_sends_wire_body_and_returns_id(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    route = mock_router.post("v1/establishment").mock(
        return_value=httpx.Response(200, json={"estabelecimentoId": ESTABLISHMENT_ID})
    )

    result = client.establishments.create(new_create_request())

    assert result.establishment_id == ESTABLISHMENT_ID

    body = json.loads(route.calls.last.request.content)
    assert body["documento"] == "12345678000199"
    assert body["razaoSocial"] == "Loja Centro LTDA"
    assert body["modeloDesembolso"] == 1
    assert body["responsavel"]["celular"] == "+5511999998888"
    assert body["contaBancaria"]["tipoConta"] == 1
    assert body["endereco"]["cep"] == "01310100"


def test_get_maps_establishment(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.get(f"v1/establishment/{ESTABLISHMENT_ID}").mock(
        return_value=httpx.Response(200, json=ESTABLISHMENT_WIRE)
    )

    establishment = client.establishments.get(ESTABLISHMENT_ID)

    assert establishment.establishment_id == ESTABLISHMENT_ID
    assert establishment.trade_name == "Loja Centro"
    assert establishment.is_active is True
    assert establishment.disbursement_model == DisbursementModel.ESTABLISHMENT_CHAIN
    assert establishment.owner.phone == "+5511999998888"
    assert establishment.bank_account is not None
    assert establishment.bank_account.account_type == BankAccountType.CURRENT
    assert establishment.address is not None
    assert establishment.address.city == "São Paulo"


def test_get_without_bank_account_and_address(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    wire = {**ESTABLISHMENT_WIRE, "modeloDesembolso": None, "contaBancaria": None, "endereco": None, "ativa": False}
    mock_router.get(f"v1/establishment/{ESTABLISHMENT_ID}").mock(return_value=httpx.Response(200, json=wire))

    establishment = client.establishments.get(ESTABLISHMENT_ID)

    assert establishment.is_active is False
    assert establishment.disbursement_model is None
    assert establishment.bank_account is None
    assert establishment.address is None


def test_list_builds_query_string(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    route = mock_router.get("v1/establishment/list").mock(return_value=httpx.Response(200, json=[ESTABLISHMENT_WIRE]))

    establishments = client.establishments.list(ListEstablishmentsRequest(trade_name="Centro", is_active=True))

    assert len(establishments) == 1
    assert establishments[0].trade_name == "Loja Centro"

    query = route.calls.last.request.url.params
    assert query["nomeFantasia"] == "Centro"
    assert query["ativa"] == "true"


def test_list_without_filters_sends_no_query(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    route = mock_router.get("v1/establishment/list").mock(return_value=httpx.Response(200, json=[]))

    assert client.establishments.list() == []
    assert not route.calls.last.request.url.params


def test_list_inactive_sends_false(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    route = mock_router.get("v1/establishment/list").mock(return_value=httpx.Response(200, json=[]))

    client.establishments.list(ListEstablishmentsRequest(is_active=False))

    assert route.calls.last.request.url.params["ativa"] == "false"


def test_update_sends_only_editable_fields(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    route = mock_router.put(f"v1/establishment/{ESTABLISHMENT_ID}").mock(return_value=httpx.Response(200))

    client.establishments.update(ESTABLISHMENT_ID, UpdateEstablishmentRequest(trade_name="Loja Centro Matriz"))

    body = json.loads(route.calls.last.request.content)
    assert body["nomeFantasia"] == "Loja Centro Matriz"
    assert body["modeloDesembolso"] is None
    assert body["endereco"] is None
    assert "contaBancaria" not in body


def test_update_bank_account_uses_own_endpoint(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    route = mock_router.put(f"v1/establishment/{ESTABLISHMENT_ID}/bank-account").mock(
        return_value=httpx.Response(200)
    )

    client.establishments.update_bank_account(
        ESTABLISHMENT_ID,
        EstablishmentBankAccount(
            bank_number="237",
            agency_number="4321",
            account_number="98765",
            account_digit="1",
            account_type=BankAccountType.SAVINGS,
        ),
    )

    body = json.loads(route.calls.last.request.content)
    assert body["banco"] == "237"
    assert body["tipoConta"] == 2


def test_activate_sends_true(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    route = mock_router.put(f"v1/establishment/{ESTABLISHMENT_ID}/status").mock(return_value=httpx.Response(200))

    client.establishments.activate(ESTABLISHMENT_ID)

    assert json.loads(route.calls.last.request.content) == {"ativa": True}


def test_deactivate_sends_false(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    route = mock_router.put(f"v1/establishment/{ESTABLISHMENT_ID}/status").mock(return_value=httpx.Response(200))

    client.establishments.deactivate(ESTABLISHMENT_ID)

    assert json.loads(route.calls.last.request.content) == {"ativa": False}


def test_create_conflict_raises_api_error(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.post("v1/establishment").mock(
        return_value=httpx.Response(
            409, json={"tipo": "Establishment.DocumentAlreadyAdded", "detalhe": "Documento já cadastrado."}
        )
    )

    with pytest.raises(ParceleMaisApiError) as exc:
        client.establishments.create(new_create_request())

    assert exc.value.status_code == 409


def test_get_not_found_raises_api_error(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.get(f"v1/establishment/{ESTABLISHMENT_ID}").mock(
        return_value=httpx.Response(
            404, json={"tipo": "Establishment.EstablishmentNotFound", "detalhe": "Estabelecimento não encontrado."}
        )
    )

    with pytest.raises(ParceleMaisApiError) as exc:
        client.establishments.get(ESTABLISHMENT_ID)

    assert exc.value.status_code == 404
