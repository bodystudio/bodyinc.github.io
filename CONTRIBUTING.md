# Contributing Guidelines

## Commit Messages

Use Conventional Commits:

```text
<type>(optional-scope): <short summary>
```

Examples:

```text
feat(site): update parent company home page
fix(site): correct canonical metadata
ci(site): tighten static checks
```

## Branch Naming

Use the Body Studio branch prefix:

```text
codex/<short-task-slug>
```

## Pull Requests

- Keep PRs focused.
- Use markdown links for every referenced file, plan, artifact, or runbook.
- Include local verification results.
- Keep content inside this repo's static-site boundary.

## Site Changes

- Preserve `site/CNAME` as exactly `body.inc`.
- Do not add contact forms, mailto links, analytics scripts, payment flows, auth surfaces, backend calls, or a second waitlist intake.
- Do not publish unsupported investor, hiring, clinical, HIPAA, SOC 2, or regulatory claims.
- Route consumer membership interest to `https://body.studio/` and `https://body.studio/waitlist.html`.
