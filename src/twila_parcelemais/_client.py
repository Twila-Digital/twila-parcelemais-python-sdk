from ._internal.auth.access_token_provider import AccessTokenProvider
from ._internal.auth.token_api_client import TokenApiClient
from ._internal.http.api_request_executor import ApiRequestExecutor
from .config.client_options import ParceleMaisClientOptions, resolve_client_options
from .customers.client import CustomersClient
from .orders.client import OrdersClient
from .simulations.client import SimulationsClient
from .establishments.client import EstablishmentsClient
from .webhooks.client import WebhooksClient


class ParceleMaisClient:
    """Cliente principal do SDK — thread-safe, deve ser reaproveitado como singleton na aplicação."""

    def __init__(self, options: ParceleMaisClientOptions) -> None:
        resolved = resolve_client_options(options)

        self._token_api_client = TokenApiClient(resolved.base_url, resolved.resilience.attempt_timeout_ms / 1000)
        token_provider = AccessTokenProvider(self._token_api_client, resolved.client_id, resolved.client_secret)

        self._executor = ApiRequestExecutor(resolved.base_url, token_provider, resolved.resilience)

        self.orders = OrdersClient(self._executor, resolved.resilience.invoice_upload_attempt_timeout_ms)
        self.simulations = SimulationsClient(self._executor)
        self.customers = CustomersClient(self._executor)
        self.establishments = EstablishmentsClient(self._executor)
        self.webhooks = WebhooksClient(self._executor)

    def close(self) -> None:
        self._executor.close()
        self._token_api_client.close()

    def __enter__(self) -> "ParceleMaisClient":
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()
