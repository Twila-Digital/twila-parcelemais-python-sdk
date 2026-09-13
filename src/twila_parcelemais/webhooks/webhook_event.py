import hashlib
import hmac
import json
import time
from typing import Optional

from ..errors.webhook_signature_error import ParceleMaisWebhookSignatureError
from ..orders.types import OrderStatus
from .types import OrderWebhookEvent

_REPLAY_TOLERANCE_SECONDS = 5 * 60


def parse_webhook_event(
    raw_json: str,
    signature_header: Optional[str] = None,
    signing_secret: Optional[str] = None,
) -> OrderWebhookEvent:
    if signature_header is not None and signing_secret is not None:
        _verify_signature(raw_json, signature_header, signing_secret)

    try:
        wire = json.loads(raw_json)
    except (ValueError, TypeError) as error:
        raise ParceleMaisWebhookSignatureError("O corpo do webhook está vazio ou não é um JSON válido.") from error

    if not isinstance(wire, dict):
        raise ParceleMaisWebhookSignatureError("O corpo do webhook está vazio ou não é um JSON válido.")

    return OrderWebhookEvent(
        order_id=wire["id_pedido"],
        status=OrderStatus.from_wire_value(wire["enum_status"]),
        status_raw=wire["enum_status"],
        status_name=wire["status"],
    )


def compute_webhook_signature(signing_secret: str, timestamp_seconds: int, payload: str) -> str:
    signed_content = f"{timestamp_seconds}.{payload}".encode()
    return hmac.new(signing_secret.encode("utf-8"), signed_content, hashlib.sha256).hexdigest()


def _verify_signature(raw_json: str, signature_header: str, signing_secret: str) -> None:
    timestamp, signature = _parse_signature_header(signature_header)
    computed = compute_webhook_signature(signing_secret, timestamp, raw_json)

    if not hmac.compare_digest(computed, signature):
        raise ParceleMaisWebhookSignatureError("A assinatura do webhook não confere.")

    event_time_seconds = timestamp
    if abs(time.time() - event_time_seconds) > _REPLAY_TOLERANCE_SECONDS:
        raise ParceleMaisWebhookSignatureError(
            "O timestamp do webhook está fora da janela de tolerância — possível replay."
        )


def _parse_signature_header(signature_header: str) -> tuple[int, str]:
    timestamp: Optional[int] = None
    signature: Optional[str] = None

    for part in signature_header.split(","):
        key, _, value = part.partition("=")
        key = key.strip()
        value = value.strip()

        if key == "t":
            try:
                timestamp = int(value)
            except ValueError:
                pass
        elif key == "v1":
            signature = value.lower()

    if timestamp is None or signature is None:
        raise ParceleMaisWebhookSignatureError(f"Cabeçalho de assinatura malformado: '{signature_header}'.")

    return timestamp, signature
