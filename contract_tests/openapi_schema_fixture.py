from functools import lru_cache
from typing import Any, Dict

import httpx

SWAGGER_URL = "https://api.staging.parcelemais.com.br/integration/swagger/v1/swagger.json"


@lru_cache(maxsize=1)
def fetch_staging_schema() -> Dict[str, Any]:
    response = httpx.get(SWAGGER_URL, timeout=30.0)

    if response.status_code != 200:
        raise RuntimeError(f"Falha ao buscar o swagger.json de staging: HTTP {response.status_code}")

    return response.json()
