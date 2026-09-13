"""Sample standalone: sem framework, script direto."""

import os

from twila_parcelemais import (
    ParceleMaisClient,
    ParceleMaisClientOptions,
    ParceleMaisEnvironment,
    SimulateInstallmentsRequest,
)


def main() -> None:
    with ParceleMaisClient(
        ParceleMaisClientOptions(
            client_id=os.environ["PARCELEMAIS_CLIENT_ID"],
            client_secret=os.environ["PARCELEMAIS_CLIENT_SECRET"],
            environment=ParceleMaisEnvironment.STAGING,
        )
    ) as client:
        parcelas = client.simulations.simulate_installments(SimulateInstallmentsRequest(requested_amount=1500.0))

        for parcela in parcelas:
            print(f"{parcela.term}x de {parcela.installment_amount} (total {parcela.total_amount})")


if __name__ == "__main__":
    main()
