# SmartCore LLM Proxy

[](https://github.com/aaserag1/SmartCore-LLM-Proxy/actions/workflows/ci.yml)
[License: MIT](https://www.google.com/search?q=LICENSE)
[](https://www.python.org/)
[PRs Welcome](https://www.google.com/search?q=CONTRIBUTING.md)

An OpenAI-compatible local gateway that routes LLM requests through LiteLLM, retries transient failures, and falls back from Gemini to DeepSeek without changing your application's API integration.

> اقرأ [الدليل العربي](https://www.google.com/search?q=README.ar.md).

## Architecture & Routing Flow

```mermaid
flowchart LR
    Client["Client App\n(Hermes AI / Open WebUI / Cline / SDK)"]
    Gateway["SmartCore Gateway\nhttp://127.0.0.1:4000/v1"]

    subgraph FastRoute ["Model: smart-core"]
        GFlash["Primary: Gemini 2.5 Flash"]
        DSChat["Fallback: DeepSeek Chat"]
        GFlash -->|"Retry / Timeout / 429"| DSChat
    end

    subgraph ReasonRoute ["Model: smart-reasoning"]
        GPro["Primary: Gemini 2.5 Pro"]
        DSReason["Fallback: DeepSeek Reasoner"]
        GPro -->|"Retry / Timeout / 429"| DSReason
    end

    Client -->|"Bearer LITELLM_MASTER_KEY"| Gateway
    Gateway --> FastRoute
    Gateway --> ReasonRoute
```

## Why SmartCore?

- One OpenAI-compatible endpoint for Hermes AI, Open WebUI, Cline, Continue.dev, scripts, and backend services.
- Automatic retries, request timeouts, context-window fallbacks, and provider fallback (`smart-core` for fast chat, `smart-reasoning` for deep reasoning).
- Provider credentials are read from environment variables, never stored in the tracked configuration.
- Localhost-only defaults, one-command `.env` initialization (`--init`), and built-in gateway diagnostics (`--doctor`).
- Windows, macOS, Linux, and Docker Compose launch options with synchronized LiteLLM versions.
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

Initialize `.env` automatically (creates `.env` from `.env.example` and generates a secure `LITELLM_MASTER_KEY`):

```bash
python scripts/start_proxy.py --init
```

Then open `.env` and fill in your provider keys:

- `GEMINI_API_KEY`: your Google AI Studio API key.
- `DEEPSEEK_API_KEY`: your DeepSeek API key.
- `LITELLM_MASTER_KEY`: auto-generated private gateway key beginning with `sk-`.

The tracked [config.yaml](https://www.google.com/search?q=config.yaml) contains only environment-variable references. Never commit `.env` or real credentials.

### 3. Validate, diagnose, and run

```bash
python scripts/start_proxy.py --check-only
python scripts/start_proxy.py --doctor
python scripts/start_proxy.py
```

If you only have one provider key configured so far, you can start in partial-provider mode:

```bash
python scripts/start_proxy.py --allow-partial-providers
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

### 4. Connect a client (Hermes AI, Open WebUI, Cline, Continue)

Use these values in any OpenAI-compatible client:

| Setting | Value |
| --- | --- |
| Base URL | `http://127.0.0.1:4000/v1` |
| API key | The value of `LITELLM_MASTER_KEY` |
| Model | `smart-core` (fast) or `smart-reasoning` (deep reasoning) |

Test the gateway:

```bash
curl http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer YOUR_LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"smart-core","messages":[{"role":"user","content":"Hello!"}]}'
```

| Model Group | Primary Model | Fallback Model | Use Case |
| --- | --- | --- | --- |
| `smart-core` | `gemini/gemini-2.5-flash` | `deepseek/deepseek-chat` | Fast everyday chat & coding |
| `smart-reasoning` | `gemini/gemini-2.5-pro` | `deepseek/deepseek-reasoner` | Complex analysis & reasoning |

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

## Customize routing & diagnostics

Edit `config.yaml` to add a provider or deployment. Keep every credential as an `os.environ/VARIABLE_NAME` reference.

Deployments sharing the same `model_name` form a load-balanced pool. A different model group can be placed in `router_settings.fallbacks` or `router_settings.context_window_fallbacks`. Run this after every change:

```bash
python scripts/check_config.py config.yaml
```

Use `--check-env` to also verify that all referenced variables are populated, or run the doctor script to inspect config, environment secrets, and live gateway endpoints:

```bash
python scripts/check_config.py config.yaml --env-file .env --check-env
python scripts/doctor.py
```

See the [LiteLLM provider documentation](https://docs.litellm.ai/docs/providers) for supported provider prefixes and parameters.

## Security notes

- Keep the default `127.0.0.1` host unless you intentionally add TLS, firewall rules, and proper access controls.
- Do not reuse a provider API key as `LITELLM_MASTER_KEY`.
- Rotate any key that has been printed, committed, or shared accidentally.
- Dependencies and the Docker image are pinned intentionally and verified to match in CI. Review release notes before upgrading them.
- Read [SECURITY.md](SECURITY.md) before reporting a vulnerability.

## Contributing

Issues and pull requests are welcome! Check the [open issues](https://www.google.com/search?q=https://github.com/aaserag1/SmartCore-LLM-Proxy/issues) for `good first issue` tasks, read [CONTRIBUTING.md](https://www.google.com/search?q=CONTRIBUTING.md), follow the [Code of Conduct](https://www.google.com/search?q=CODE_OF_CONDUCT.md), and run:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/check_config.py config.yaml
```

## License

Released under the [MIT License](https://www.google.com/search?q=LICENSE).

Created by Ahmed Adel (Abo Adel) and open to community contributions.
