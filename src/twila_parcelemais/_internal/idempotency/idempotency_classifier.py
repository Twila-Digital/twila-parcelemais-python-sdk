_MUTABLE_PATHS_REQUIRING_IDEMPOTENCY_KEY = (
    "v1/order/start-cdc-sale",
    "v1/order/invoice",
    "v1/order",
    "v1/webhooks",
)


def requires_idempotency_key(method: str, path: str) -> bool:
    if method.upper() != "POST":
        return False

    return any(path.endswith(mutable_path) for mutable_path in _MUTABLE_PATHS_REQUIRING_IDEMPOTENCY_KEY)


def is_retry_safe(method: str, path: str, has_idempotency_key: bool) -> bool:
    upper_method = method.upper()

    if upper_method in ("GET", "HEAD", "OPTIONS"):
        return True

    if upper_method in ("PUT", "DELETE"):
        return "v1/webhooks/" in path

    if upper_method != "POST":
        return False

    return requires_idempotency_key(method, path) and has_idempotency_key
