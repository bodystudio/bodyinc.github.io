# Body Inc Corporate Website

This repository contains the static parent-company website for **Body Inc.** at [https://body.inc](https://body.inc). The separate [Body Studio public site](https://github.com/bodystudio/bodystudio.github.io) remains the consumer membership and waitlist surface for [https://body.studio](https://body.studio).

## Site Structure

| Path | Purpose |
| --- | --- |
| `site/index.html` | Lean Body Inc parent-company home page. |
| `site/CNAME` | GitHub Pages custom domain, exactly `body.inc`. |
| `site/robots.txt` | Public crawl policy and sitemap pointer. |
| `site/sitemap.xml` | Sitemap for the corporate home page. |
| `site/assets/` | Static visual and favicon assets only. |

## Contract

- Static HTML/CSS assets only, with no build step.
- GitHub Pages hosting only.
- No backend, auth, analytics stack, payment flow, contact form, second CRM intake source, or Azure runtime.
- Consumer membership interest routes to [https://body.studio/](https://body.studio/) and [https://body.studio/waitlist.html](https://body.studio/waitlist.html).
- Harness exemption is recorded in [spec-contract.yaml](spec-contract.yaml) and validated by [tooling/validate_hygiene_contract.py](tooling/validate_hygiene_contract.py).
- Site content constraints are validated by [tooling/check_static_site.py](tooling/check_static_site.py).

## Development

```bash
cd site
python3 -m http.server 8080
```

Then open [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

## Verification

```bash
python3 tooling/validate_hygiene_contract.py
python3 tooling/check_static_site.py --root .
python3 -m unittest
git diff --check
```

## Deployment

Changes merged to `main` deploy through GitHub Pages using the workflow in [.github/workflows/deploy.yml](.github/workflows/deploy.yml). The deployment emits a machine-readable Pages proof artifact.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
