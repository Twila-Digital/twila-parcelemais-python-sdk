"""Sample Flask: ParceleMaisClient como singleton na app factory, fechado no teardown."""

import os

from flask import Flask, jsonify

from twila_parcelemais import (
    ParceleMaisApiError,
    ParceleMaisClient,
    ParceleMaisClientOptions,
    ParceleMaisEnvironment,
    SimulateInstallmentsRequest,
)


def create_app() -> Flask:
    app = Flask(__name__)

    app.parcelemais_client = ParceleMaisClient(
        ParceleMaisClientOptions(
            client_id=os.environ["PARCELEMAIS_CLIENT_ID"],
            client_secret=os.environ["PARCELEMAIS_CLIENT_SECRET"],
            environment=ParceleMaisEnvironment.STAGING,
        )
    )

    @app.teardown_appcontext
    def _close_client(_exception: object = None) -> None:
        pass  # o client é fechado no shutdown do processo, não por request

    @app.get("/simulacoes")
    def simulate() -> object:
        try:
            parcelas = app.parcelemais_client.simulations.simulate_installments(
                SimulateInstallmentsRequest(requested_amount=1500.0)
            )
        except ParceleMaisApiError as error:
            return jsonify({"erro": str(error)}), error.status_code

        return jsonify(
            [
                {"prazo": p.term, "valorParcela": p.installment_amount, "valorTotal": p.total_amount}
                for p in parcelas
            ]
        )

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
