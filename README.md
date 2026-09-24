<p align="center">
  <img src="https://raw.githubusercontent.com/Twila-Digital/twila-parcelemais-python-sdk/production/assets/logo-light.svg" alt="Parcele+" width="180" style="max-width: 100%;">
</p>

<p align="center">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/Twila-Digital/twila-parcelemais-python-sdk"></a>
  <a href="https://github.com/Twila-Digital/twila-parcelemais-python-sdk/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/Twila-Digital/twila-parcelemais-python-sdk/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/Twila-Digital/twila-parcelemais-python-sdk/actions/workflows/quality.yml"><img alt="Quality" src="https://github.com/Twila-Digital/twila-parcelemais-python-sdk/actions/workflows/quality.yml/badge.svg"></a>
  <a href="https://github.com/Twila-Digital/twila-parcelemais-python-sdk/security/code-scanning"><img alt="Security" src="https://github.com/Twila-Digital/twila-parcelemais-python-sdk/actions/workflows/security.yml/badge.svg"></a>
  <a href="https://codecov.io/gh/Twila-Digital/twila-parcelemais-python-sdk"><img alt="Coverage" src="https://codecov.io/gh/Twila-Digital/twila-parcelemais-python-sdk/branch/production/graph/badge.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9%2B-539E43">
</p>

# twila-parcelemais

SDK oficial em Python para a API do [Parcele+](https://www.cartaosimples.com.br) — crédito direto ao consumidor (CDC) e parcelamento no momento da compra.

> Uso restrito a server-side. O `client_secret` nunca deve ser embarcado em um app mobile, SPA ou qualquer código que rode no navegador/dispositivo do usuário final.

## Compatibilidade

| Runtime | Versões aceitas |
| --- | --- |
| Python | 3.9 ou superior (CI cobre 3.9, 3.10, 3.11, 3.12, 3.13 e 3.14) |

Cliente síncrono, baseado em [httpx](https://www.python-httpx.org/), com tipos totalmente anotados (`py.typed`, PEP 561).

## Instalação

```bash
pip install twila-parcelemais
```

## Quick start

```python
from twila_parcelemais import ParceleMaisClient, ParceleMaisClientOptions, ParceleMaisEnvironment

client = ParceleMaisClient(
    ParceleMaisClientOptions(
        client_id="<seu-client-id>",
        client_secret="<seu-client-secret>",
        environment=ParceleMaisEnvironment.STAGING,
    )
)
```

`ParceleMaisClient` é thread-safe e deve ser reaproveitado como singleton na sua aplicação — ele mantém o cache do token de acesso e o estado do circuit breaker. Feche-o só no shutdown (`client.close()`, ou use como context manager: `with ParceleMaisClient(options) as client:`).

### Simulando parcelas

```python
from twila_parcelemais import SimulateInstallmentsRequest

parcelas = client.simulations.simulate_installments(SimulateInstallmentsRequest(requested_amount=1500.0))

for parcela in parcelas:
    print(f"{parcela.term}x de {parcela.installment_amount} (total {parcela.total_amount})")
```

### Criando um pedido

```python
from twila_parcelemais import CreateOrderRequest, OrderAddress

pedido_id = client.orders.create(
    CreateOrderRequest(
        cpf="12345678901",
        phone_number="+5511999998888",
        establishment_document="12345678000195",
        requested_amount=1500.0,
        name="Maria Souza",
        email="maria.souza@exemplo.com.br",
        date_of_birth="1990-05-20T00:00:00-03:00",
        address=OrderAddress(
            street="Av. Paulista",
            number="1578",
            neighborhood="Bela Vista",
            city="São Paulo",
            state="SP",
            postal_code="01311000",
        ),
    )
)
```

`create` retorna só o `id` do pedido — a API não devolve o pedido completo na criação; use `client.orders.get(pedido_id)` se precisar dos dados completos logo em seguida.

## Clientes por recurso

| Cliente | Métodos |
| --- | --- |
| `client.orders` | `create`, `get`, `list`, `start_cdc_sale`, `import_invoice` |
| `client.simulations` | `simulate_installments`, `simulate_values` |
| `client.customers` | `get`, `list` |
| `client.establishments` | `create`, `get`, `list`, `update`, `update_bank_account`, `activate`, `deactivate` |
| `client.webhooks` | `create`, `list`, `list_audit`, `update`, `delete` |

## Paginação

`orders.list(...)`, `customers.list(...)` e `webhooks.list_audit(...)` retornam um `PagedResult[T]` — sem auto-paginação, você controla explicitamente o avanço de página:

```python
from twila_parcelemais import ListOrdersRequest

page = client.orders.list(ListOrdersRequest(page=1, page_size=20))

for order in page.items:
    print(order.id)

if page.has_next:
    next_page = client.orders.list(ListOrdersRequest(page=2, page_size=20))
```

## Tratamento de erros

| Erro | Quando |
| --- | --- |
| `ParceleMaisConfigurationError` | Configuração do `ParceleMaisClient` inválida (ex: `client_id`/`client_secret` ausentes) |
| `ParceleMaisAuthenticationError` | Falha ao gerar/renovar o token de acesso |
| `ParceleMaisValidationError` | `400` — erro de validação, com `field_errors` por campo |
| `ParceleMaisRateLimitError` | `429` |
| `ParceleMaisTimeoutError` | Timeout de rede, timeout total, ou circuit breaker aberto |
| `ParceleMaisApiError` | Qualquer outro erro de API (`404`, `409`, `5xx`) |
| `ParceleMaisWebhookSignatureError` | Assinatura de webhook inválida ou expirada |

```python
from twila_parcelemais import ParceleMaisApiError

try:
    client.orders.get(order_id)
except ParceleMaisApiError as error:
    print(f"{error.status_code} {error.error_code}: {error}")
```

## Validando webhooks

```python
from twila_parcelemais import parse_webhook_event

evento = parse_webhook_event(raw_body, signature_header, signing_secret)
```

Verifica a assinatura HMAC-SHA256 do cabeçalho e a janela de replay (5 minutos) antes de expor o evento. Lança `ParceleMaisWebhookSignatureError` se a assinatura for inválida ou o evento estiver fora da janela.

## Samples

- `samples/sample_plain` — script standalone, sem framework
- `samples/sample_flask` — `ParceleMaisClient` como singleton na app factory do Flask

## Qualidade, segurança e cobertura

- **Build/Test** (`ci.yml`) — `mypy --strict` + suíte de testes (`pytest` + `respx`) em Python 3.9–3.14.
- **Quality** (`quality.yml`) — análise estática via Codacy CLI (pylint), resultados publicados na aba **Security → Code scanning** do repositório.
- **Security** (`security.yml`) — [CodeQL](https://codeql.github.com/) para Python, rodando a cada PR/push e semanalmente.
- **Coverage** — cobertura de testes coletada via `pytest-cov` e publicada no [Codecov](https://codecov.io/gh/Twila-Digital/twila-parcelemais-python-sdk).

## Documentação completa

[documentacao.parcelemais.com.br](https://documentacao.parcelemais.com.br) — referência de todos os endpoints, autenticação, webhooks e mais.

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Código de conduta

Este projeto segue o [Código de Conduta](CODE_OF_CONDUCT.md).

## Licença

[MIT](LICENSE)
