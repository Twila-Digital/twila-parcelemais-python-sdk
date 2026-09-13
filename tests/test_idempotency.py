import pytest

from twila_parcelemais._internal.idempotency.idempotency_classifier import is_retry_safe, requires_idempotency_key


@pytest.mark.parametrize(
    "method,path,expected",
    [
        ("POST", "v1/order", True),
        ("POST", "v1/order/start-cdc-sale", True),
        ("POST", "v1/order/invoice", True),
        ("POST", "v1/webhooks", True),
        ("POST", "v1/order/simulate-installments", False),
        ("GET", "v1/order", False),
    ],
)
def test_requires_idempotency_key(method: str, path: str, expected: bool) -> None:
    assert requires_idempotency_key(method, path) is expected


@pytest.mark.parametrize(
    "method,path,has_key,expected",
    [
        ("GET", "v1/order/123", False, True),
        ("HEAD", "v1/order", False, True),
        ("PUT", "v1/webhooks/1", False, True),
        ("DELETE", "v1/webhooks/1", False, True),
        ("PUT", "v1/order/123", False, False),
        ("POST", "v1/order", True, True),
        ("POST", "v1/order", False, False),
        ("POST", "v1/order/simulate-values", False, False),
    ],
)
def test_is_retry_safe(method: str, path: str, has_key: bool, expected: bool) -> None:
    assert is_retry_safe(method, path, has_key) is expected
