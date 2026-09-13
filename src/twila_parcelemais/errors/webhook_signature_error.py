from .base import ParceleMaisError


class ParceleMaisWebhookSignatureError(ParceleMaisError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
