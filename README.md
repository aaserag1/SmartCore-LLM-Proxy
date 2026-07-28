# SmartCore LLM Proxy

[![CI](https://github.com/aaserag1/SmartCore-LLM-Proxy/actions/workflows/ci.yml/badge.svg)](https://github.com/aaserag1/SmartCore-LLM-Proxy/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)

An OpenAI-compatible local gateway that routes LLM requests through LiteLLM, retries transient failures, and falls back from Gemini to DeepSeek without changing your application's API integration.

> اقرأ [الدليل العربي](README.ar.md).

## Why SmartCore?

- One OpenAI-compatible endpoint for Hermes AI, Open WebUI, scripts, and backend services.
- Automatic retries, cooldowns, and provider fallback.
- Provider credentials are read from environment variables, never stored in the tracked configuration.
- Localhost-only defaults and gateway authentication.
- Windows, macOS, Linux, and Docker Compose launch options.
- Configuration validation and GitHub Actions checks for safer contributions.

SmartCore improves resilience, but it cannot guarantee uptime: availability still depends on your network, provider accounts, quotas, and the models you configure.

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/aaserag1/SmartCore-LLM-Proxy.git
cd SmartCore-LLM-Proxy
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install the pinned dependency:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Configure secrets

Copy the example file:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Fill in:

- `GEMINI_API_KEY`: your Google AI Studio API key.
- `DEEPSEEK_API_KEY`: your DeepSeek API key.
- `LITELLM_MASTER_KEY`: a private gateway key beginning with `sk-`.

Generate a strong gateway key with:

```bash
python -c "import secrets; print('sk-' + secrets.token_urlsafe(32))"
```

The tracked [`config.yaml`](config.yaml) contains only environment-variable references. Never commit `.env` or real credentials.

### 3. Validate and run

```bash
python scripts/start_proxy.py --check-only
python scripts/start_proxy.py
```

Platform shortcuts are also available:

```powershell
# Windows
.\Run_LiteLLM.bat
# or
.\run.ps1
```

```bash
# macOS / Linux
./run.sh
```

The default endpoint is `http://127.0.0.1:4000/v1`.

### 4. Connect a client

Use these values in Hermes AI or another OpenAI-compatible client:

| Setting | Value |
| --- | --- |
| Base URL | `http://127.0.0.1:4000/v1` |
| API key | The value of `LITELLM_MASTER_KEY` |
| Model | `smart-core` |

Test the gateway:

```bash
curl http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer YOUR_LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"smart-core","messages":[{"role":"user","content":"Hello!"}]}'
```

`smart-core` uses Gemini 2.5 Flash first. After retryable failures, LiteLLM falls back to `deepseek-chat`.

## Docker Compose

Docker Compose uses the same `.env` and `config.yaml`:

```bash
docker compose up -d
docker compose ps
docker compose logs -f smartcore
```

Stop it with:

```bash
docker compose down
```

The container port is published only on `127.0.0.1` by default.

## Customize routing

Edit `config.yaml` to add a provider or deployment. Keep every credential as an `os.environ/VARIABLE_NAME` reference.

Deployments sharing the same `model_name` form a load-balanced pool. A different model group can be placed in `router_settings.fallbacks`. Run this after every change:

```bash
python scripts/check_config.py config.yaml
```

Use `--check-env` to also verify that all referenced variables are populated:

```bash
python scripts/check_config.py config.yaml --env-file .env --check-env
```

See the [LiteLLM provider documentation](https://docs.litellm.ai/docs/providers) for supported provider prefixes and parameters.

## Security notes

- Keep the default `127.0.0.1` host unless you intentionally add TLS, firewall rules, and proper access controls.
- Do not reuse a provider API key as `LITELLM_MASTER_KEY`.
- Rotate any key that has been printed, committed, or shared accidentally.
- Dependencies and the Docker image are pinned intentionally. Review release notes before upgrading them.
- Read [SECURITY.md](SECURITY.md) before reporting a vulnerability.

## Contributing

Issues and pull requests are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md), follow the [Code of Conduct](CODE_OF_CONDUCT.md), and run:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/check_config.py config.yaml
```

## License

Released under the [MIT License](LICENSE).

Created by Ahmed Adel (Abo Adel) and open to community contributions.
