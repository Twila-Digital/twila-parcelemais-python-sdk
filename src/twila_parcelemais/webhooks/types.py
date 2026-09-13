from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from ..orders.types import OrderStatus


class WebHookType(IntEnum):
    CUSTOMER = 1
    SIMULATION = 2
    ORDER = 3
    UNKNOWN = -1

    @classmethod
    def from_wire_value(cls, value: int) -> "WebHookType":
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


class WebHookAuthenticationType(IntEnum):
    NONE = 1
    BASIC = 2
    JWT = 3
    UNKNOWN = -1

    @classmethod
    def from_wire_value(cls, value: int) -> "WebHookAuthenticationType":
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


@dataclass(frozen=True)
class Webhook:
    type: WebHookType
    url: str
    authentication_type: WebHookAuthenticationType


@dataclass(frozen=True)
class CreateWebhookRequest:
    type: WebHookType
    url: str
    authentication_type: WebHookAuthenticationType
    credential: Optional[str] = None


@dataclass(frozen=True)
class CreateWebhookResult:
    signing_secret: str


@dataclass(frozen=True)
class UpdateWebhookRequest:
    url: str
    authentication_type: WebHookAuthenticationType
    credential: Optional[str] = None


@dataclass(frozen=True)
class OrderWebhookEvent:
    order_id: str
    status: OrderStatus
    status_raw: int
    status_name: str
