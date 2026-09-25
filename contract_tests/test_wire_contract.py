import re

import pytest
from openapi_schema_fixture import fetch_staging_schema

EXPECTED_PATHS = [
    "/v1/authentication/accesstoken",
    "/v1/order",
    "/v1/order/{id}",
    "/v1/order/paged",
    "/v1/order/start-cdc-sale",
    "/v1/order/invoice",
    "/v1/order/simulate-installments",
    "/v1/order/simulate-values",
    "/v1/customer/{id}",
    "/v1/customer/paged",
    "/v1/webhooks",
    "/v1/webhooks/{type}",
    "/v1/webhooks/auditoria",
]


def _normalize(template_path: str) -> str:
    return re.sub(r"\{[^}]+}", "", template_path)


def _simple_type_name(schema_key: str) -> str:
    return schema_key.rsplit(".", 1)[-1]


@pytest.mark.parametrize("expected_path", EXPECTED_PATHS)
def test_endpoint_exists_in_staging_schema(expected_path: str) -> None:
    schema = fetch_staging_schema()
    paths = list((schema.get("paths") or {}).keys())

    matches = any(_normalize(real_path).endswith(_normalize(expected_path)) for real_path in paths)

    assert matches, (
        f"Endpoint '{expected_path}' não encontrado no swagger.json de staging — o SDK e o backend divergiram."
    )


def test_order_response_schema_has_fields_order_mapper_expects() -> None:
    schema = fetch_staging_schema()
    schemas = (schema.get("components") or {}).get("schemas") or {}

    order_schema_entry = next(
        (value for key, value in schemas.items() if _simple_type_name(key) == "OrderIntegrationResponse"), None
    )

    assert order_schema_entry is not None, "Não encontrei o schema OrderIntegrationResponse no swagger.json de staging."

    properties = order_schema_entry.get("properties") or {}

    for expected_field in ["id", "numero", "status", "documentoCliente", "criadoEm"]:
        assert expected_field in properties, (
            f"Campo '{expected_field}' esperado pelo mapper não existe (mais) no schema de staging."
        )
