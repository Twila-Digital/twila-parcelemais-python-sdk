from typing import Any, Callable, TypeVar

from ...paged_result import PagedResult

T = TypeVar("T")


def paged_result_from_wire(wire: dict[str, Any], item_mapper: Callable[[dict[str, Any]], T]) -> PagedResult[T]:
    pagina = wire["pagina"]
    return PagedResult(
        items=[item_mapper(item) for item in wire["itens"]],
        has_next=pagina["tem_proximo"],
        has_previous=pagina["tem_anterior"],
        page_number=pagina["numero"],
        page_size=pagina["tamanho"],
        total_count=pagina["total"],
    )
