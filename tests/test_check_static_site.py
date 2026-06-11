#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[1]
SCRIPT_PATH = REPO_ROOT / "tooling/check_static_site.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_static_site", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestCheckStaticSite(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_module()

    def test_current_site_passes(self) -> None:
        self.assertEqual(self.mod.evaluate(REPO_ROOT), [])

    def test_flags_non_body_inc_cname(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._copy_minimal_site(root)
            (root / "site/CNAME").write_text("body.studio\n", encoding="utf-8")
            findings = self.mod.evaluate(root)
            self.assertIn("site/CNAME must contain exactly body.inc", findings)

    def test_flags_contact_form(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._copy_minimal_site(root)
            index = root / "site/index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace("</main>", "<form></form></main>"),
                encoding="utf-8",
            )
            findings = self.mod.evaluate(root)
            self.assertIn("site/index.html contains forbidden static-site snippet: <form", findings)
            self.assertIn("site/index.html must not contain forms", findings)

    def test_flags_unapproved_external_link(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._copy_minimal_site(root)
            index = root / "site/index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace("https://body.studio/", "https://example.com/"),
                encoding="utf-8",
            )
            findings = self.mod.evaluate(root)
            self.assertIn("site/index.html links to unapproved external URL: https://example.com/", findings)

    def test_flags_light_blue_theme_token(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._copy_minimal_site(root)
            styles = root / "site/styles.css"
            styles.write_text(
                styles.read_text(encoding="utf-8") + "\n.lightBlue { color: #b7d7d8; }\n",
                encoding="utf-8",
            )
            findings = self.mod.evaluate(root)
            self.assertIn("site/styles.css contains forbidden light-blue theme snippet: #b7d7d8", findings)

    def _copy_minimal_site(self, root: Path) -> None:
        for path in (
            "spec-contract.yaml",
            "site/CNAME",
            "site/robots.txt",
            "site/sitemap.xml",
            "site/index.html",
            "site/styles.css",
            "site/assets/body-inc-card.svg",
            "site/assets/body-studio-250-hudson.webp",
            "site/assets/favicon.svg",
        ):
            source = REPO_ROOT / path
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix in {".webp", ".png", ".jpg"}:
                target.write_bytes(source.read_bytes())
            else:
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        (root / "README.md").write_text("spec-contract.yaml\n", encoding="utf-8")
        (root / "AGENTS.md").write_text("static site\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
