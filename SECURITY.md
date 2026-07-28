# Security Policy

## Supported version

Security fixes are applied to the latest version on the `main` branch.

## Reporting a vulnerability

Do not open a public issue containing vulnerability details, credentials, private prompts, or provider responses.

Use GitHub's **Report a vulnerability** option in the repository's Security tab when it is available. If private vulnerability reporting is unavailable, open a public issue containing only a request for a private maintainer contact channel and no technical details.

Include, privately:

- A concise description and impact.
- Reproduction steps or a minimal proof of concept.
- Affected configuration and version, with all secrets removed.
- Any suggested mitigation.

The maintainer will acknowledge a usable report, investigate it, and coordinate disclosure when a fix is ready.

## Deployment guidance

- Keep the gateway bound to `127.0.0.1` unless it is protected by TLS, a firewall, and suitable access controls.
- Set a unique, strong `LITELLM_MASTER_KEY` and do not reuse provider keys.
- Never commit `.env` or inline credentials in YAML.
- Pin and review dependency versions before upgrades.
- If a secret is exposed, revoke and rotate it immediately. Removing it from the latest commit is not enough because Git history and logs may retain it.
