import httpx
import respx

from twila_parcelemais import ParceleMaisClient, SimulateInstallmentsRequest, SimulateValuesRequest


def test_simulate_installments_maps_response(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.get("v1/order/simulate-installments").mock(
        return_value=httpx.Response(200, json=[{"valorTotalDebito": 1600.0, "prazo": 3, "valorParcela": 533.33}])
    )

    parcelas = client.simulations.simulate_installments(SimulateInstallmentsRequest(requested_amount=1500.0))

    assert len(parcelas) == 1
    assert parcelas[0].term == 3
    assert parcelas[0].installment_amount == 533.33


def test_simulate_values_maps_response(mock_router: respx.MockRouter, client: ParceleMaisClient) -> None:
    mock_router.get("v1/order/simulate-values").mock(
        return_value=httpx.Response(
            200,
            json={
                "valoresEstabelecimento": {"valorVenda": 1500.0, "valorDesembolso": 1450.0},
                "valoresCliente": {"valorParcela": 533.33},
            },
        )
    )

    result = client.simulations.simulate_values(SimulateValuesRequest(amount=1500.0, term=3))

    assert result.sale_amount == 1500.0
    assert result.disbursement_amount == 1450.0
    assert result.installment_amount == 533.33
