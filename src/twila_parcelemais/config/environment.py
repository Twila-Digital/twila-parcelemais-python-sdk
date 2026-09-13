from enum import Enum


class ParceleMaisEnvironment(str, Enum):
    STAGING = "staging"
    PRODUCTION = "production"


_BASE_URLS = {
    ParceleMaisEnvironment.STAGING: "https://api.staging.parcelemais.com.br/integration/",
    ParceleMaisEnvironment.PRODUCTION: "https://api.parcelemais.com.br/integration/",
}


def environment_base_url(environment: ParceleMaisEnvironment) -> str:
    return _BASE_URLS[environment]
