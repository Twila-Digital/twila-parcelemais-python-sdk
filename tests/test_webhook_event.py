import json
import time

import pytest

from twila_parcelemais import OrderStatus, ParceleMaisWebhookSignatureError
from twila_parcelemais.webhooks.webhook_event import compute_webhook_signature, parse_webhook_event

SIGNING_SECRET = "whsec_test"


def _raw_event(order_id: str = "order-1", status: int = 9, status_name: str = "Comprado") -> str:
    return json.dumps({"id_pedido": order_id, "enum_status": status, "status": status_name})


def test_parse_without_signature_maps_fields() -> None:
    event = parse_webhook_event(_raw_event())

    assert event.order_id == "order-1"
    assert event.status is OrderStatus.PURCHASED
    assert event.status_raw == 9
    assert event.status_name == "Comprado"


def test_parse_maps_unknown_status_to_unknown_enum_member() -> None:
    event = parse_webhook_event(_raw_event(status=999))

    assert event.status is OrderStatus.UNKNOWN
    assert event.status_raw == 999


def test_parse_invalid_json_raises_signature_error() -> None:
    with pytest.raises(ParceleMaisWebhookSignatureError):
        parse_webhook_event("not json")


def test_valid_signature_passes_verification() -> None:
    payload = _raw_event()
    timestamp = int(time.time())
    signature = compute_webhook_signature(SIGNING_SECRET, timestamp, payload)
    header = f"t={timestamp},v1={signature}"

    event = parse_webhook_event(payload, header, SIGNING_SECRET)

    assert event.order_id == "order-1"


def test_invalid_signature_raises_error() -> None:
    payload = _raw_event()
    timestamp = int(time.time())
    header = f"t={timestamp},v1={'0' * 64}"

    with pytest.raises(ParceleMaisWebhookSignatureError):
        parse_webhook_event(payload, header, SIGNING_SECRET)


def test_expired_timestamp_raises_replay_error() -> None:
    payload = _raw_event()
    old_timestamp = int(time.time()) - 6 * 60
    signature = compute_webhook_signature(SIGNING_SECRET, old_timestamp, payload)
    header = f"t={old_timestamp},v1={signature}"

    with pytest.raises(ParceleMaisWebhookSignatureError):
        parse_webhook_event(payload, header, SIGNING_SECRET)


def test_malformed_signature_header_raises_error() -> None:
    with pytest.raises(ParceleMaisWebhookSignatureError):
        parse_webhook_event(_raw_event(), "garbage-header", SIGNING_SECRET)
