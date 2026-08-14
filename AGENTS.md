# AGENTS.md

Django 5.2.4 hotel management app (Hostal Rivera). Single app `reservas` contains all models, views, forms, templates. Docs, code comments, and commit messages are in Spanish — keep them that way. The codebase was cleaned up to look professional on GitHub; avoid adding new teaching-style or emoji comments.

## Setup gotchas (read first)

- The local `.venv` has **no project dependencies installed** and runs Python 3.14. CI and Django 5.2 target **Python 3.11–3.13** — recreate the venv with a supported version before installing (`pip install -r requirements.txt`).
- There is no `.env`, and settings **fail fast**: with `DEBUG=False` (the default) and a missing/insecure `SECRET_KEY`, every `manage.py` command raises `ImproperlyConfigured`. For local work either copy `.env.example` to `.env` and set `DEBUG=True`, or export env vars like CI does (`DEBUG=True`, `SECRET_KEY=...`, `ALLOWED_HOSTS=localhost,127.0.0.1`).
- `requirements.txt` is the source of truth (Django==5.2.4).

## Verification

Run the test suite and linting to verify changes:

```bash
python manage.py check          # catches config/import errors
python manage.py test reservas  # 47 tests
pylint $(git ls-files '*.py')   # needs: pip install pylint pylint-django polib + env vars set
```

Pylint uses `.pylintrc` (pylint_django plugin, max-line-length=130, migrations and `manage.py` excluded). Pylint needs the same env vars as manage.py because it imports Django settings.

## i18n

- 3 languages: `es` (default, no URL prefix), `gl`, `en` — URLs are wrapped in `i18n_patterns(prefix_default_language=False)`.
- Prefer `python manage.py compilemessages` (msgfmt is available on this machine). `compile_mo.py` is a portable fallback that reads from the project `locale/` directory or from `COMPILE_MO_LOCALE_PATH`.
- Compiled `.mo` files **are committed to git** — recompile and commit them together with `.po` changes.

## Architecture notes that change how you work

- Admin URL is env-configurable: `ADMIN_PATH` (default `admin/`), resolved in `hotel_project/urls.py`.
- Rate limiting: `@ratelimit` decorators in `reservas/views.py` + `reservas/middleware.py::RatelimitMiddleware` renders `reservas/error_ratelimit.html` with HTTP 429. New POST endpoints should get a rate limit.
- DB is env-driven: SQLite by default, PostgreSQL in production (`DB_ENGINE`/`DB_NAME`/...). Static files served by WhiteNoise (`STORAGES['staticfiles']['BACKEND']` = CompressedManifest).
- SES Hospedajes (mandatory Spanish police traveler reporting): `Reserva.ses_hospedajes_*` fields and `ViajeroCheckin` model exist; the flow is documented in `GUIA_SES_HOSPEDAJES_CHECKIN.md`. DNI/NIE validation lives in `reservas/models.py::validar_dni_nie` (python-stdnum).
- Deploy: Dokploy on a VPS, Gunicorn + WhiteNoise — see `dokploy.md` and `DEPLOYMENT.md` before touching deploy config.

## CI

GitHub Actions on `main`: `django.yml` (`manage.py test`, Python 3.10–3.12), `pylint.yml` (on every push), `codeql.yml`. CI injects env vars (`DEBUG=True`, dummy `SECRET_KEY`, SQLite) — mirror them locally when debugging CI failures.
