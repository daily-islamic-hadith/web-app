# Repository Guidelines

## Project Structure & Module Organization

The Flask application lives in `server/hadith_app/`. `app.py` registers application-level behavior; feature endpoints are in `routes/` and `auth/`; business logic is in `service/`; and persistence code is in `dao/` and `db/`. Keep new API work layered similarly rather than querying the database from route handlers. Server-rendered pages, styles, and browser scripts live in `templates/` and `static/`. The SQLite database at `server/hadith_app/db/app.db` is tracked; handle changes to it deliberately. Root-level `scripts/` contains data import, crawling, and AI-explanation maintenance utilities.

## Build, Test, and Development Commands

From `server/`, use Python 3.10+ and a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask --app hadith_app run
```

The final command starts the local site and API at `http://127.0.0.1:5000/`. Dependency versions are pinned in `server/requirements.txt`; update that file whenever a runtime dependency changes. Run data scripts from the repository root, for example `python3 scripts/setup_hadith_db.py`, only after reviewing their database effects.

## Coding Style & Naming Conventions

Follow the existing Python style: four-space indentation, `snake_case` for functions, variables, modules, and route helpers, and `PascalCase` for classes/schemas. Keep imports grouped at the top and use short docstrings where behavior is non-obvious. Preserve the current frontend conventions: lowercase, hyphenated CSS classes and JavaScript filenames such as `static/js/scripts.js`. No formatter or linter is configured; make focused changes consistent with neighboring code.

## Testing Guidelines

No repository test suite or coverage target is currently configured. For each change, run the server locally and exercise the affected page or API path, including error behavior where relevant. Add focused `pytest` tests under `server/tests/` for new non-trivial logic; name files `test_<feature>.py` and tests `test_<behavior>()`. Do not claim automated coverage that has not been added.

## Commit & Pull Request Guidelines

History uses short, imperative summaries such as `add share hadith Url btn` and `fix loading Google Analytics key in the page`; use a concise lowercase action-oriented subject (for example, `add user profile endpoint`). Keep commits scoped to one concern. Pull requests should explain the user-facing or API impact, link the relevant issue when available, list validation performed, and include screenshots for template, CSS, or JavaScript changes. Never commit `.env`, virtual environments, credentials, or unreviewed production database changes.
