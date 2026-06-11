#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[1]
SCRIPT_PATH = REPO_ROOT / "tooling/emit_pages_deploy_proof.py"


def load_module():
    spec = importlib.util.spec_from_file_location("emit_pages_deploy_proof", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestEmitPagesDeployProof(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module()

    def test_build_payload_records_public_pages_deploy_state(self) -> None:
        payload = self.mod.build_payload(
            status="passed",
            reason="github_pages_deploy_succeeded",
            page_url="https://body.inc/",
            env={
                "GITHUB_REPOSITORY": "bodystudio/bodyinc.github.io",
                "GITHUB_WORKFLOW": "Deploy to GitHub Pages",
                "GITHUB_RUN_ID": "123",
                "GITHUB_RUN_ATTEMPT": "1",
                "GITHUB_RUN_NUMBER": "42",
                "GITHUB_SHA": "abc123",
                "GITHUB_REF": "refs/heads/main",
                "GITHUB_EVENT_NAME": "push",
            },
        )

        self.assertEqual(payload["artifact_type"], "bodyinc.github_io.pages_deploy_proof")
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["reason"], "github_pages_deploy_succeeded")
        self.assertEqual(payload["deployment_model"], "static-site")
        self.assertEqual(payload["provider"], "github-pages")
        self.assertEqual(payload["environment"], "github-pages")
        self.assertEqual(payload["page_url"], "https://body.inc/")
        self.assertEqual(payload["page_url_configured"], True)
        self.assertEqual(payload["github"]["repository"], "bodystudio/bodyinc.github.io")

    def test_main_writes_json_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "proof.json"
            rc = self.mod.main(
                [
                    "--status",
                    "passed",
                    "--reason",
                    "github_pages_deploy_succeeded",
                    "--page-url",
                    "https://body.inc/",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(rc, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["artifact_type"], "bodyinc.github_io.pages_deploy_proof")
            self.assertEqual(payload["page_url_configured"], True)

    def test_main_rejects_success_without_page_url(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "proof.json"
            with self.assertRaises(SystemExit):
                self.mod.main(
                    [
                        "--status",
                        "passed",
                        "--reason",
                        "github_pages_deploy_succeeded",
                        "--page-url",
                        " ",
                        "--output",
                        str(output),
                    ]
                )

            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
