#!/usr/bin/env python3
"""Validate the harness exemption hygiene contract for bodyinc.github.io."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    contract_path = ROOT / "spec-contract.yaml"
    schema_path = ROOT / "schemas/governance/hygiene-contract.schema.json"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(contract), key=lambda err: err.path)
    if errors:
        print("hygiene contract validation failed")
        for err in errors:
            pointer = "/".join(str(part) for part in err.absolute_path)
            print(f"- {pointer or '<root>'}: {err.message}")
        return 1

    if contract.get("harness_exempt") is not True:
        print("harness_exempt must remain true for this repository")
        return 1

    print("Hygiene contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
