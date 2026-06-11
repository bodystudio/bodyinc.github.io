# Implementation Traceability

This repo implements the Body Inc parent corporate site plan.

## Source Plan

- [PLAN-2026-06-11-body-inc-parent-corporate-site.md](https://github.com/bodystudio/body-plans/blob/main/plans/active/PLAN-2026-06-11-body-inc-parent-corporate-site.md)

## Boundary Decisions

- `bodyinc.github.io` owns the static parent-company site for `https://body.inc/`.
- `bodystudio.github.io` remains the consumer membership and waitlist site for `https://body.studio/`.
- The site has no backend, auth, analytics stack, payment flow, contact form, second CRM intake source, or Azure runtime.
- Consumer interest routes only to `https://body.studio/` and `https://body.studio/waitlist.html`.

## Verification

Run:

```bash
python3 tooling/validate_hygiene_contract.py
python3 tooling/check_static_site.py --root .
python3 -m unittest
git diff --check
```
