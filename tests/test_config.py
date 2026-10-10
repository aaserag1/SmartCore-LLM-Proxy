from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_config import (  # noqa: E402
    load_env_file,
    parse_env_file,
    read_config,
    validate_config,
)
from start_proxy import find_litellm_executable  # noqa: E402


class ConfigValidationTests(unittest.TestCase):
    def test_repository_config_is_valid(self) -> None:
        config = read_config(ROOT / "config.yaml")
        errors, references = validate_config(config)

        self.assertEqual(errors, [])
        self.assertEqual(
            references,
            {"GEMINI_API_KEY", "DEEPSEEK_API_KEY", "LITELLM_MASTER_KEY"},
        )

    def test_inline_credentials_are_rejected(self) -> None:
        config = read_config(ROOT / "config.yaml")
        config["model_list"][0]["litellm_params"]["api_key"] = "real-secret"

        errors, _ = validate_config(config)

        self.assertTrue(any("do not store credentials" in error for error in errors))

    def test_unknown_fallback_is_rejected(self) -> None:
        config = read_config(ROOT / "config.yaml")
        config["router_settings"]["fallbacks"] = [
            {"smart-core": ["missing-model"]}
        ]

        errors, _ = validate_config(config)

        self.assertTrue(any("unknown fallback model" in error for error in errors))

    def test_environment_check_reports_empty_values(self) -> None:
        config = read_config(ROOT / "config.yaml")
        clean_environment = {
            key: value
            for key, value in os.environ.items()
            if key
            not in {"GEMINI_API_KEY", "DEEPSEEK_API_KEY", "LITELLM_MASTER_KEY"}
        }

        with patch.dict(os.environ, clean_environment, clear=True):
            errors, _ = validate_config(config, check_environment=True)

        self.assertEqual(
            sum("missing or empty" in error for error in errors),
            3,
        )

    def test_parse_env_file_returns_empty_mapping_for_missing_or_comment_only_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            self.assertEqual(parse_env_file(directory_path / "missing.env"), {})

            env_path = directory_path / ".env"
            env_path.write_text("\n # comment\n\t# another comment\n", encoding="utf-8")
            self.assertEqual(parse_env_file(env_path), {})

    def test_parse_env_file_rejects_missing_equals_and_invalid_names(self) -> None:
        cases = [
            ("NO_VALUE\n", "expected KEY=VALUE"),
            ("1INVALID=value\n", "invalid variable name '1INVALID'"),
            ("export =value\n", "invalid variable name ''"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            for content, message in cases:
                with self.subTest(content=content):
                    env_path.write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, rf"{env_path}:1: {message}"):
                        parse_env_file(env_path)

    def test_env_loader_supports_export_quotes_and_preserves_process_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text(
                "export FIRST=\"one\"\nSECOND='two'\nEXISTING=file\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {"EXISTING": "process"}, clear=True):
                values = load_env_file(env_path)
                self.assertEqual(values["FIRST"], "one")
                self.assertEqual(os.environ["FIRST"], "one")
                self.assertEqual(os.environ["SECOND"], "two")
                self.assertEqual(os.environ["EXISTING"], "process")

    def test_litellm_console_script_is_discoverable_when_installed(self) -> None:
        if importlib.util.find_spec("litellm") is None:
            self.skipTest("LiteLLM is not installed in the validation-only environment")

        executable = find_litellm_executable()

        self.assertIsNotNone(executable)
        self.assertTrue(Path(executable).is_file())


if __name__ == "__main__":
    unittest.main()
