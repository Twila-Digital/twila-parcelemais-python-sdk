from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from ..orders.types import DateLike, OrderStatus


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
class WebhookAudit:
    id: str
    type: WebHookType
    request: str
    response: str
    status_code: int
    created_at: str


@dataclass(frozen=True)
class ListWebhookAuditRequest:
    start_date: Optional[DateLike] = None
    end_date: Optional[DateLike] = None
    order_id: Optional[str] = None
    order_number: Optional[int] = None
    status_code: Optional[int] = None
    page: int = 1
    page_size: int = 10


@dataclass(frozen=True)
class OrderWebhookEvent:
    order_id: str
    status: OrderStatus
    status_raw: int
    status_name: str
