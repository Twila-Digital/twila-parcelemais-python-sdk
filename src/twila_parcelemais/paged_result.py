from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PagedResult(Generic[T]):
    items: list[T]
    has_next: bool
    has_previous: bool
    page_number: int
    page_size: int
    total_count: int
