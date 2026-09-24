from ._client import ParceleMaisClient
from .config.client_options import ParceleMaisClientOptions
from .config.environment import ParceleMaisEnvironment
from .config.resilience_options import ParceleMaisResilienceOptions
from .customers.client import CustomersClient
from .customers.types import Address as CustomerAddress
from .customers.types import Customer, ListCustomersRequest
from .errors import (
    ParceleMaisApiError,
    ParceleMaisAuthenticationError,
    ParceleMaisConfigurationError,
    ParceleMaisError,
    ParceleMaisRateLimitError,
    ParceleMaisTimeoutError,
    ParceleMaisValidationError,
    ParceleMaisWebhookSignatureError,
    ProblemDetails,
)
from .establishments.client import EstablishmentsClient
from .establishments.types import (
    BankAccountType,
    CreateEstablishmentRequest,
    CreateEstablishmentResult,
    DisbursementModel,
    Establishment,
    EstablishmentAddress,
    EstablishmentBankAccount,
    EstablishmentOwner,
    ListEstablishmentsRequest,
    UpdateEstablishmentRequest,
)
from .orders.client import OrdersClient
from .orders.types import Address as OrderAddress
from .orders.types import (
    CheckoutLink,
    CreateOrderRequest,
    InvoiceFile,
    ListOrdersRequest,
    Order,
    OrderStatus,
)
from .paged_result import PagedResult
from .simulations.client import SimulationsClient
from .simulations.types import (
    CalculationValueType,
    InstallmentSimulation,
    SimulateInstallmentsRequest,
    SimulateValuesRequest,
    ValuesSimulation,
)
from .webhooks.client import WebhooksClient
from .webhooks.types import (
    CreateWebhookRequest,
    CreateWebhookResult,
    OrderWebhookEvent,
    UpdateWebhookRequest,
    Webhook,
    WebHookAuthenticationType,
    WebHookType,
)
from .webhooks.webhook_event import compute_webhook_signature, parse_webhook_event

__version__ = "1.0.0"

__all__ = [
    "ParceleMaisClient",
    "ParceleMaisClientOptions",
    "ParceleMaisEnvironment",
    "ParceleMaisResilienceOptions",
    "PagedResult",
    # errors
    "ParceleMaisError",
    "ParceleMaisApiError",
    "ParceleMaisAuthenticationError",
    "ParceleMaisConfigurationError",
    "ParceleMaisRateLimitError",
    "ParceleMaisTimeoutError",
    "ParceleMaisValidationError",
    "ParceleMaisWebhookSignatureError",
    "ProblemDetails",
    # orders
    "OrdersClient",
    "OrderStatus",
    "OrderAddress",
    "CreateOrderRequest",
    "Order",
    "ListOrdersRequest",
    "CheckoutLink",
    "InvoiceFile",
    # simulations
    "SimulationsClient",
    "CalculationValueType",
    "SimulateInstallmentsRequest",
    "SimulateValuesRequest",
    "InstallmentSimulation",
    "ValuesSimulation",
    # customers
    "CustomersClient",
    "CustomerAddress",
    "Customer",
    "ListCustomersRequest",
    # establishments
    "EstablishmentsClient",
    "DisbursementModel",
    "BankAccountType",
    "EstablishmentOwner",
    "EstablishmentBankAccount",
    "EstablishmentAddress",
    "Establishment",
    "CreateEstablishmentRequest",
    "CreateEstablishmentResult",
    "UpdateEstablishmentRequest",
    "ListEstablishmentsRequest",
    # webhooks
    "WebhooksClient",
    "WebHookType",
    "WebHookAuthenticationType",
    "Webhook",
    "CreateWebhookRequest",
    "CreateWebhookResult",
    "UpdateWebhookRequest",
    "OrderWebhookEvent",
    "parse_webhook_event",
    "compute_webhook_signature",
]
