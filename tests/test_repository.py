from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent


class RepositoryTests(unittest.TestCase):
    def test_expected_community_files_exist(self) -> None:
        expected = [
            "README.md",
            "README.ar.md",
            "LICENSE",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "SECURITY.md",
            ".github/pull_request_template.md",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
        ]
        for relative_path in expected:
            with self.subTest(path=relative_path):
                self.assertTrue((ROOT / relative_path).is_file())

    def test_env_files_are_ignored_but_example_is_tracked(self) -> None:
        ignore_rules = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".env", ignore_rules)
        self.assertIn("!.env.example", ignore_rules)

    def test_all_yaml_files_parse(self) -> None:
        yaml_files = list(ROOT.rglob("*.yml")) + list(ROOT.rglob("*.yaml"))
        self.assertTrue(yaml_files)
        for path in yaml_files:
            if ".git" in path.parts:
                continue
            with self.subTest(path=path.relative_to(ROOT)):
                with path.open(encoding="utf-8") as stream:
                    yaml.safe_load(stream)

    def test_compose_binds_gateway_to_localhost(self) -> None:
        compose = yaml.safe_load(
            (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        )
        ports = compose["services"]["smartcore"]["ports"]
        self.assertTrue(all(str(port).startswith("127.0.0.1:") for port in ports))


if __name__ == "__main__":
    unittest.main()
