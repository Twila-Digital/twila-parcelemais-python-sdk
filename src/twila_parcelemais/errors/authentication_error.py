from typing import Optional

from .base import ParceleMaisError


class ParceleMaisAuthenticationError(ParceleMaisError):
    def __init__(self, message: str, cause: Optional[BaseException] = None) -> None:
        super().__init__(message, cause)
