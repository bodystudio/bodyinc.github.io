# AGENTS.md

## Repository Role
- `bodyinc.github.io` is the public static parent-company web surface for Body Inc.
- It publishes the GitHub Pages site for `https://body.inc/`.

## Boundary
- This repo owns static corporate site assets, repo-local hygiene tooling, and GitHub Pages deployment automation only.
- It does not own the Body Studio consumer membership site, CRM waitlist runtime, auth, analytics, payments, provider integrations, clinical workflows, or private operational evidence.
- `bodystudio.github.io` remains the public consumer site for `https://body.studio/`.
- This repo is `harness_exempt: true` and does not run replay/signing harness flows.

## Guardrails
- Keep the site static: no backend, auth, analytics stack, payment flow, contact form, second waitlist source, or Azure runtime.
- Keep `site/CNAME` exactly `body.inc`; do not add wildcard DNS guidance.
- Route consumer membership interest to `https://body.studio/` and `https://body.studio/waitlist.html`.
- Do not invent or publish a contact mailbox.
- Do not add secrets, PHI, employment-confidential material, provider-auth material, commercial secrets, internal-ops records, production exports, private keys, Apple signing assets, provider credentials, raw legal files, Delaware filings, sensitive screenshots, or source binaries.
- Avoid unsupported investor, hiring, clinical, HIPAA, SOC 2, or regulatory claims.
- Changes here must pass deterministic static-site hygiene checks in CI.
- This repo uses a local `merge_gate` aggregate job during bootstrap so the first site PR is not blocked on org reusable-workflow access.
- Codex work for this repo is coordinated from the local Mac using repo-scoped worktrees under `/Users/chase/Github/bodystudio/worktrees`; read this repo's `AGENTS.md` before work, then consult `body-plans` plans and `body-infra/infra/github/repo_profiles.yaml` when available for cross-repo context.
- PR description file references must use markdown links.
- If proof requires macOS, Xcode, simulator/device, hardware, signing, org settings, provider account credentials, governed provider setup, branch protection changes, or local-only secrets, collect evidence from the local Mac or required human-approved control plane; do not claim completion from static repo checks alone.
```yaml
failure_class_source:
  - AGENTS.md
  - spec-contract.yaml
  - .github/workflows
context_source:
  - site
  - docs
  - tooling
remediation_steps:
  - Keep changes scoped to static site assets, docs, hygiene tooling, and deployment automation.
  - Re-run the static site hygiene checks before opening a PR.
  - Route CRM, auth, analytics, payment, runtime policy, contract, and private evidence changes to the owning repo.
reverify_command: python3 tooling/validate_hygiene_contract.py && python3 tooling/check_static_site.py --root . && python3 -m unittest
autonomy:
  primary_dev_tool: codex-mac
  mode: bounded-autonomous
  subagent_allowed: true
  subagent_roots:
    - site/**
    - docs/**
    - tooling/**
    - tests/**
    - .github/workflows/**
  cross_repo_write_policy: deny
  protected_paths:
    - AGENTS.md
    - spec-contract.yaml
    - .github/workflows/**
  escalation_triggers:
    - deployment_policy_change
    - runtime_policy_request
    - private_artifact_request
    - contact_destination_request
  requires_plan_artifact: true
```

## Required Checks
```yaml
profile_source: body-infra/infra/github/repo_profiles.yaml
required_statuses:
  - validate_hygiene_contract
  - check_static_site
  - merge_gate
merge_gate_role: aggregator
local_verify:
  fast: python3 tooling/validate_hygiene_contract.py && python3 tooling/check_static_site.py --root . && python3 -m unittest tests/test_emit_pages_deploy_proof.py tests/test_check_static_site.py
  full: python3 tooling/validate_hygiene_contract.py && python3 tooling/check_static_site.py --root . && python3 -m unittest
```

## Profile and Stack State
```yaml
repo_profile: static-site
current_state_profile: static-site
target_state_profile: static-site
transition_phase: steady
current_stack: static-site
target_stack: static-site
bundle_mode: optional
attestation_mode: exempt
conformance_focus: runtime
correct_mode: diagnose-only
pin_files: []
overlays:
  - policy-surface
  - public-web
migration_owner: null
migration_deadline: null
```
