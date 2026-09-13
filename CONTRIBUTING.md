# Contribuindo

## Pré-requisitos

- Python 3.9+
- `pip`

## Build e testes

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

mypy
ruff check .
pytest
```

Os contract tests (`contract_tests/`) fazem uma chamada real ao OpenAPI de staging e não rodam por padrão:

```bash
pip install -e ".[dev]" -e "./contract_tests"
pytest contract_tests
```

## Instalando a partir do código-fonte

Enquanto o pacote não é publicado no PyPI, instale direto do repositório:

```bash
pip install git+https://github.com/Twila-Digital/twila-parcelemais-python-sdk.git@production
```

Ou clone e instale em modo editável (`pip install -e .`) a partir de uma cópia local.

## Abrindo um PR

1. Crie uma branch a partir de `production`
2. Adicione testes para qualquer mudança de comportamento
3. Rode `mypy && ruff check . && pytest` localmente antes de abrir o PR
4. Abra o PR contra `production` — o CI roda testes automaticamente

## Release (publicação no PyPI)

O PyPI suporta **Trusted Publishing (OIDC)** desde 2023 — o mais maduro entre os registries que usamos. A action oficial [`pypa/gh-action-pypi-publish`](https://github.com/pypa/gh-action-pypi-publish) troca o token OIDC do GitHub Actions por uma credencial de publish de curta duração, sem precisar de um token de longa duração guardado como secret.

Antes do primeiro release, alguém com acesso à conta/organização do PyPI precisa configurar um **Trusted Publisher** (funciona mesmo com o projeto ainda não existindo no PyPI — "pending publisher"):

- Em [pypi.org](https://pypi.org/manage/account/publishing/) (ou na página do projeto, se ele já existir): **Add a pending publisher**
  - **PyPI Project Name:** `twila-parcelemais`
  - **Owner:** `Twila-Digital`
  - **Repository name:** `twila-parcelemais-python-sdk`
  - **Workflow name:** `release.yml`
  - **Environment name:** `production`

No repositório do GitHub, criar o [environment](https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment) `production` (Settings → Environments) com **Required reviewers** configurado. Nenhum secret de registry é necessário — a credencial de publish inteira vem do OIDC em runtime.

Com isso configurado, `git push --tags` numa tag `v*` (ex.: `v1.0.0`) dispara build → testes → contract tests → **pausa esperando aprovação manual do `environment` `production`** → publish no PyPI (Trusted Publishing) → GitHub Release.

O primeiro `pypi-publish` via OIDC contra um "pending publisher" já cria o projeto no PyPI — não precisa de um publish manual prévio (diferente do npm).

## Reportando problemas

Abra uma [issue](https://github.com/Twila-Digital/twila-parcelemais-python-sdk/issues) com passos para reproduzir, versão do pacote/Python e o comportamento esperado vs. observado. Nunca inclua `client_id`/`client_secret` reais no relato.
