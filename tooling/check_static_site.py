#!/usr/bin/env python3
"""Validate the static Body Inc corporate site contract."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import urlparse
from xml.etree import ElementTree


EXPECTED_DOMAIN = "https://body.inc/"
APPROVED_EXTERNAL_LINKS = {
    EXPECTED_DOMAIN,
    "https://body.studio/",
    "https://body.studio/waitlist.html",
}
FORBIDDEN_SITE_SNIPPETS = (
    "api.body.studio",
    "mailto:",
    "<form",
    "stripe",
    "checkout",
    "analytics",
    "gtag",
    "segment",
    "hubspot",
    "investor",
    "investment",
    "careers",
    "hiring",
    "hipaa",
    "soc 2",
    "fda",
    "regulated",
    "clinical-grade",
)
FORBIDDEN_STYLE_SNIPPETS = (
    "#b7d7d8",
    "lightblue",
    "light blue",
    "--aqua",
)


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonical_href: str | None = None
        self.og_url: str | None = None
        self.og_image: str | None = None
        self.links: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.scripts: list[str] = []
        self.forms = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name.lower(): value or "" for name, value in attrs}
        if tag == "a":
            self.links.append((attr_map.get("href", ""), attr_map.get("aria-label", "")))
        if tag == "img":
            self.images.append(attr_map)
        if tag == "script":
            self.scripts.append(attr_map.get("src", ""))
        if tag == "form":
            self.forms += 1
        if tag == "meta" and attr_map.get("property") == "og:url":
            self.og_url = attr_map.get("content")
        if tag == "meta" and attr_map.get("property") == "og:image":
            self.og_image = attr_map.get("content")
        if tag == "link":
            rel = {part.strip().lower() for part in attr_map.get("rel", "").split()}
            if "canonical" in rel:
                self.canonical_href = attr_map.get("href")


def _glob_exists(root: Path, pattern: str) -> bool:
    return any(True for _ in root.glob(pattern))


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _html_files(root: Path) -> Iterable[Path]:
    return sorted((root / "site").glob("*.html"))


def _local_ref_exists(root: Path, html_path: Path, ref: str) -> bool:
    ref = ref.split("#", 1)[0].split("?", 1)[0]
    if not ref or ref.startswith(("https://", "http://", "mailto:", "tel:")):
        return True
    if ref.startswith("/"):
        target = root / "site" / ref.lstrip("/")
    else:
        target = html_path.parent / ref
    if target.is_dir():
        target = target / "index.html"
    return target.exists()


def evaluate(root: Path) -> list[str]:
    findings: list[str] = []

    cname = root / "site/CNAME"
    if not cname.exists():
        findings.append("missing file: site/CNAME")
    elif cname.read_text(encoding="utf-8").strip() != "body.inc":
        findings.append("site/CNAME must contain exactly body.inc")

    contract = root / "spec-contract.yaml"
    if not contract.exists():
        findings.append("missing file: spec-contract.yaml")
    else:
        txt = contract.read_text(encoding="utf-8")
        for expected in ('repository: "bodyinc.github.io"', "harness_exempt: true", "- \"check_static_site\""):
            if expected not in txt:
                findings.append(f"spec-contract.yaml missing expected contract text: {expected}")
        for pattern in ("README.md", "site/CNAME", "site/index.html", "site/assets/**"):
            if not _glob_exists(root, pattern):
                findings.append(f"required path pattern has no matches: {pattern}")

    robots = root / "site/robots.txt"
    if not robots.exists():
        findings.append("missing file: site/robots.txt")
    else:
        robots_txt = robots.read_text(encoding="utf-8")
        if "Sitemap: https://body.inc/sitemap.xml" not in robots_txt:
            findings.append("site/robots.txt should reference https://body.inc/sitemap.xml")
        if "Disallow: /" in robots_txt:
            findings.append("site/robots.txt should not block the public site")

    sitemap = root / "site/sitemap.xml"
    if not sitemap.exists():
        findings.append("missing file: site/sitemap.xml")
    else:
        try:
            tree = ElementTree.parse(sitemap)
            namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            locs = [node.text for node in tree.findall(".//sm:loc", namespace)]
            if locs != [EXPECTED_DOMAIN]:
                findings.append("site/sitemap.xml should contain only https://body.inc/")
        except ElementTree.ParseError as exc:
            findings.append(f"site/sitemap.xml must be valid XML: {exc}")

    index = root / "site/index.html"
    if not index.exists():
        findings.append("missing file: site/index.html")
        return findings

    for css_path in sorted((root / "site").glob("*.css")):
        css = css_path.read_text(encoding="utf-8").lower()
        label = _relative(css_path, root)
        for snippet in FORBIDDEN_STYLE_SNIPPETS:
            if snippet in css:
                findings.append(f"{label} contains forbidden light-blue theme snippet: {snippet}")

    for html_path in _html_files(root):
        label = _relative(html_path, root)
        html = html_path.read_text(encoding="utf-8")
        lower = html.lower()
        for snippet in FORBIDDEN_SITE_SNIPPETS:
            if snippet in lower:
                findings.append(f"{label} contains forbidden static-site snippet: {snippet}")
        if "http://" in lower:
            findings.append(f"{label} contains mixed-content http:// reference")
        parser = SiteParser()
        parser.feed(html)
        if parser.forms:
            findings.append(f"{label} must not contain forms")
        if parser.scripts:
            findings.append(f"{label} must not load scripts")
        if parser.canonical_href != EXPECTED_DOMAIN:
            findings.append(f"{label} canonical link must be {EXPECTED_DOMAIN}")
        if parser.og_url != EXPECTED_DOMAIN:
            findings.append(f"{label} og:url must be {EXPECTED_DOMAIN}")
        if parser.og_image != "https://body.inc/assets/body-inc-card.svg":
            findings.append(f"{label} og:image must reference the Body Inc card asset")
        for href, _aria in parser.links:
            if href.startswith("https://") and href not in APPROVED_EXTERNAL_LINKS:
                findings.append(f"{label} links to unapproved external URL: {href}")
            if href.startswith("http://"):
                findings.append(f"{label} links to non-HTTPS URL: {href}")
            if not _local_ref_exists(root, html_path, href):
                findings.append(f"{label} references missing local link: {href}")
        for image in parser.images:
            src = image.get("src", "")
            if not _local_ref_exists(root, html_path, src):
                findings.append(f"{label} references missing local image: {src}")
            if not image.get("alt"):
                findings.append(f"{label} image is missing alt text: {src}")
            if not image.get("width") or not image.get("height"):
                findings.append(f"{label} image should define width and height: {src}")

    index_html = index.read_text(encoding="utf-8")
    required_copy = (
        "Body Inc.",
        "the company behind Body Studio",
        "https://body.studio/",
        "https://body.studio/waitlist.html",
    )
    for needle in required_copy:
        if needle not in index_html:
            findings.append(f"site/index.html missing required copy or link: {needle}")

    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    findings = evaluate(root)
    if findings:
        print("Static site validation failed")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Static site validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
