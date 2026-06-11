#!/usr/bin/env python3
"""Emit a structured GitHub Pages deployment proof artifact."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping


ARTIFACT_TYPE = "bodyinc.github_io.pages_deploy_proof"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def github_context(env: Mapping[str, str]) -> dict[str, str]:
    return {
        "repository": env.get("GITHUB_REPOSITORY", ""),
        "workflow": env.get("GITHUB_WORKFLOW", ""),
        "run_id": env.get("GITHUB_RUN_ID", ""),
        "run_attempt": env.get("GITHUB_RUN_ATTEMPT", ""),
        "run_number": env.get("GITHUB_RUN_NUMBER", ""),
        "sha": env.get("GITHUB_SHA", ""),
        "ref": env.get("GITHUB_REF", ""),
        "event_name": env.get("GITHUB_EVENT_NAME", ""),
    }


def build_payload(
    *,
    status: str,
    reason: str,
    page_url: str,
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    return {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": "0.1",
        "generated_at": utc_now(),
        "github": github_context(env or os.environ),
        "status": status,
        "reason": reason,
        "deployment_model": "static-site",
        "provider": "github-pages",
        "environment": "github-pages",
        "page_url": page_url,
        "page_url_configured": bool(page_url.strip()),
    }


def write_json(output_path: Path, payload: Mapping[str, object]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", required=True, choices=["passed", "failed", "held"])
    parser.add_argument("--reason", required=True)
    parser.add_argument("--page-url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.status == "passed" and not args.page_url.strip():
        raise SystemExit("--page-url is required when status is passed")
    payload = build_payload(status=args.status, reason=args.reason, page_url=args.page_url)
    write_json(args.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
