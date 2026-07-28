#!/usr/bin/env python3
"""Validate a SmartCore/LiteLLM YAML configuration without contacting providers."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only on incomplete installs
    raise SystemExit(
        "PyYAML is required. Install requirements.txt or requirements-dev.txt first."
    ) from exc


ENV_REFERENCE = re.compile(r"^os\.environ/([A-Za-z_][A-Za-z0-9_]*)$")
SENSITIVE_NAMES = {
    "api_key",
    "master_key",
    "api_token",
    "access_token",
    "secret",
    "password",
}


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse the small KEY=VALUE subset used by this project."""
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ValueError(f"{path}:{line_number}: expected KEY=VALUE")

        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ValueError(f"{path}:{line_number}: invalid variable name {name!r}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[name] = value

    return values


def load_env_file(path: Path) -> dict[str, str]:
    """Load values without replacing variables already present in the process."""
    values = parse_env_file(path)
    for name, value in values.items():
        os.environ.setdefault(name, value)
    return values


def _environment_reference(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = ENV_REFERENCE.fullmatch(value.strip())
    return match.group(1) if match else None


def _walk(value: Any, path: str = "config") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, str(key), child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def collect_environment_references(config: Any) -> set[str]:
    references: set[str] = set()
    for _, _, value in _walk(config):
        reference = _environment_reference(value)
        if reference:
            references.add(reference)
    return references


def validate_config(
    config: Any, *, check_environment: bool = False
) -> tuple[list[str], set[str]]:
    """Return validation errors and referenced environment-variable names."""
    errors: list[str] = []
    if not isinstance(config, dict):
        return ["The YAML root must be a mapping."], set()

    model_list = config.get("model_list")
    if not isinstance(model_list, list) or not model_list:
        errors.append("model_list must be a non-empty list.")
        model_list = []

    model_names: set[str] = set()
    for index, deployment in enumerate(model_list):
        label = f"model_list[{index}]"
        if not isinstance(deployment, dict):
            errors.append(f"{label} must be a mapping.")
            continue

        model_name = deployment.get("model_name")
        if not isinstance(model_name, str) or not model_name.strip():
            errors.append(f"{label}.model_name must be a non-empty string.")
        else:
            model_names.add(model_name)

        params = deployment.get("litellm_params")
        if not isinstance(params, dict):
            errors.append(f"{label}.litellm_params must be a mapping.")
            continue
        provider_model = params.get("model")
        if not isinstance(provider_model, str) or "/" not in provider_model:
            errors.append(
                f"{label}.litellm_params.model must include a provider prefix."
            )

    for path, key, value in _walk(config):
        if key.lower() not in SENSITIVE_NAMES or value in (None, ""):
            continue
        if _environment_reference(value) is None:
            errors.append(
                f"{path} must reference an environment variable; "
                "do not store credentials in YAML."
            )

    general_settings = config.get("general_settings")
    if not isinstance(general_settings, dict):
        errors.append("general_settings must be a mapping.")
    elif _environment_reference(general_settings.get("master_key")) is None:
        errors.append(
            "general_settings.master_key must use os.environ/LITELLM_MASTER_KEY."
        )

    router_settings = config.get("router_settings", {})
    if not isinstance(router_settings, dict):
        errors.append("router_settings must be a mapping.")
        router_settings = {}

    fallbacks = router_settings.get("fallbacks", [])
    if not isinstance(fallbacks, list):
        errors.append("router_settings.fallbacks must be a list.")
        fallbacks = []

    for index, fallback in enumerate(fallbacks):
        label = f"router_settings.fallbacks[{index}]"
        if not isinstance(fallback, dict) or len(fallback) != 1:
            errors.append(f"{label} must map one model group to fallback groups.")
            continue
        source, targets = next(iter(fallback.items()))
        if source not in model_names:
            errors.append(f"{label} references unknown source model {source!r}.")
        if not isinstance(targets, list) or not targets:
            errors.append(f"{label} must contain at least one fallback model.")
            continue
        for target in targets:
            if target not in model_names:
                errors.append(f"{label} references unknown fallback model {target!r}.")
            if target == source:
                errors.append(f"{label} cannot fall back to itself.")

    references = collect_environment_references(config)
    if check_environment:
        for reference in sorted(references):
            if not os.environ.get(reference, "").strip():
                errors.append(f"Environment variable {reference} is missing or empty.")

        master_key = os.environ.get("LITELLM_MASTER_KEY", "")
        if master_key and not master_key.startswith("sk-"):
            errors.append("LITELLM_MASTER_KEY must start with 'sk-'.")
        if master_key and len(master_key) < 24:
            errors.append("LITELLM_MASTER_KEY is too short; use at least 24 characters.")

    return errors, references


def read_config(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Configuration file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}: {exc}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", default="config.yaml", type=Path)
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Load KEY=VALUE pairs before checking referenced variables.",
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Require every referenced environment variable to be populated.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.env_file:
            load_env_file(args.env_file)
        config = read_config(args.config)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    errors, references = validate_config(
        config, check_environment=args.check_env
    )
    if errors:
        for error in errors:
            print(f"[ERROR] {error}", file=sys.stderr)
        return 1

    print(
        f"[OK] {args.config} is valid "
        f"({len(references)} environment variable references)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
