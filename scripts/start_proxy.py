#!/usr/bin/env python3
"""Load local secrets, validate configuration, and start LiteLLM."""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

from check_config import load_env_file, read_config, validate_config


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def find_litellm_executable() -> str | None:
    """Find the LiteLLM console script from PATH or this Python environment."""
    from_path = shutil.which("litellm")
    if from_path:
        return from_path

    scripts_directory = Path(sysconfig.get_path("scripts"))
    candidates = (
        scripts_directory / "litellm.exe",
        scripts_directory / "litellm",
    )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "config.yaml",
        help="LiteLLM YAML configuration path.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=PROJECT_ROOT / ".env",
        help="Environment file path.",
    )
    parser.add_argument("--host", help="Listener host (default: HOST or 127.0.0.1).")
    parser.add_argument("--port", type=int, help="Listener port (default: PORT or 4000).")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate configuration and secrets without starting LiteLLM.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        load_env_file(args.env_file)
        config = read_config(args.config)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    errors, references = validate_config(config, check_environment=True)
    if errors:
        print("[ERROR] SmartCore configuration is not ready:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print(
            f"Copy {PROJECT_ROOT / '.env.example'} to {args.env_file} "
            "and add your credentials.",
            file=sys.stderr,
        )
        return 1

    host = args.host or os.environ.get("HOST", "127.0.0.1")
    port = args.port or int(os.environ.get("PORT", "4000"))
    if not (1 <= port <= 65535):
        print("[ERROR] Port must be between 1 and 65535.", file=sys.stderr)
        return 1

    print(
        f"[OK] Configuration is valid ({len(references)} secret references). "
        f"Gateway: http://{host}:{port}/v1"
    )
    if args.check_only:
        return 0

    if importlib.util.find_spec("litellm") is None:
        print(
            "[ERROR] LiteLLM is not installed. Run: "
            "python -m pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    litellm_executable = find_litellm_executable()
    if not litellm_executable:
        print(
            "[ERROR] The LiteLLM command was not found in this Python environment. "
            "Reinstall requirements.txt.",
            file=sys.stderr,
        )
        return 1

    command = [
        litellm_executable,
        "--config",
        str(args.config.resolve()),
        "--host",
        host,
        "--port",
        str(port),
    ]
    print("[INFO] Starting LiteLLM. Press Ctrl+C to stop.")
    try:
        return subprocess.call(command, cwd=PROJECT_ROOT, env=os.environ.copy())
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
