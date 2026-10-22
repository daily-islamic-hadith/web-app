# Daily Islamic Hadith Web Service

Welcome to the **Daily Islamic Hadith Web Service** repository! This project is a Flask-based web application designed
to provide a
daily Hadith from the vast collections of Islamic traditions.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [Contributing](#contributing)
- [License](#license)

## Features

- **RESTful Web Service**: A backend service that provides the daily Hadith data, accessible via API.
- **Lightweight**: Minimal dependencies and lightweight code for efficient performance.
- **Open Source**: Free to use, modify, and distribute.

## Installation

### Prerequisites

Use Python 3.12.15 for deployment and Python 3.12 for local development. You can check your Python version with:

```bash
python3.12 --version
```

You should also have `pip` (Python package installer) available.

### Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/osama1225/daily-islamic-hadith.git
cd daily-islamic-hadith/server
```

### Set Up a Virtual Environment (Optional but Recommended)

Create and activate a virtual environment to manage dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### Install Dependencies

Install the necessary Python packages using `pip`:

```bash
python -m pip install --require-hashes -r requirements.lock
```

## Reproducible dependencies and checks

`requirements.txt` retains the direct runtime pins. Deploy from `requirements.lock`,
which also pins transitive packages and artifact hashes. `runtime.txt` retains the
existing deployment convention and selects Python 3.12.15. Confirm the provider and
app root before migrating runtime selection to `.python-version`.

psycopg2 builds from source. Install a C compiler, Python headers, libpq headers,
and `pg_config` first. On Debian/Ubuntu use `libpq-dev` and `gcc`. With Homebrew's
libpq and OpenSSL, set these variables before installing:

```bash
export PATH="$(brew --prefix libpq)/bin:$PATH"
export LDFLAGS="-L$(brew --prefix openssl@3)/lib"
export CPPFLAGS="-I$(brew --prefix openssl@3)/include"
```

From the repository root, install only the layers you need, together:

```bash
# Backend development and auditing:
python -m pip install --require-hashes -r server/requirements.lock -r server/requirements-dev.lock
# Also running maintenance scripts and their tests:
python -m pip install --require-hashes -r server/requirements.lock -r server/requirements-dev.lock -r scripts/requirements.lock
python -m pip check
```

The development lock includes pytest, pip-audit, and pip-tools 7.5.3. Regenerate
with Python 3.12 in the deployment environment, production first, from the root:

```bash
export CUSTOM_COMPILE_COMMAND='See server/README.md for lock regeneration commands'
pip-compile --allow-unsafe --resolver=backtracking --generate-hashes --strip-extras --output-file server/requirements.lock server/requirements.txt
pip-compile --allow-unsafe --resolver=backtracking --generate-hashes --strip-extras --output-file server/requirements-dev.lock server/requirements-dev.in
pip-compile --allow-unsafe --resolver=backtracking --generate-hashes --strip-extras --output-file scripts/requirements.lock scripts/requirements.in
```

Both additional layers constrain overlapping dependencies to the production lock.
Regenerate them whenever production changes. Review the pins and hashes, install
all required layers together in a fresh environment, and run the version check
before testing. `pip check` alone does not detect an unintended runtime upgrade.
Dependabot proposes monthly updates; regenerate and review all affected locks in
each proposal. Keep major-version proposals separate from compatible updates.

From `server/`:

```bash
python -m pytest tests/test_dependency_lock.py -q
python -m pytest tests -q
python -m flask --app hadith_app routes
python -m pip_audit --require-hashes --disable-pip -r requirements.lock -r requirements-dev.lock -r ../scripts/requirements.lock
```

Omit the script lock from the audit if that layer is not installed. Tests stub
external API calls and use disposable data. The CSV-import test skips without the
script layer. PostgreSQL integration skips unless `TEST_POSTGRES_URL` points to a
disposable database. The Linux CI workflow installs all layers, supplies a disposable
PostgreSQL instance, boots `gunicorn hadith_app:app`, and audits the dependency sets.
The lock files were generated and installed on macOS/Python 3.12.14; Linux/Python
3.12.15 CI must pass before deployment.

Never run `scripts/setup_hadith_db.py` against production as a check: it replaces
`hadith_meta` in `app.db` in the current directory. Scripts require the production
lock plus `scripts/requirements.lock`; pandas is absent from the web runtime.

For EC2 deployments, check out the release tag, install `requirements.lock` with
the service's Python 3.12 virtual environment, run `python -m pip check`, then restart
the service. `runtime.txt` does not install or upgrade Python on EC2.

CORS preserves public origins and Authorization preflights, disables cookie
credentials, and denies private-network access. Verify actual extension consumers
in staging before release. Password verification rejects inputs over 72 UTF-8 bytes;
confirm a verified account-reset path for potentially affected users before deploying
the bcrypt backend update. No stored hashes or database schema are migrated.

## Usage

### Running the Flask Application

After installing the dependencies, start the Flask application:

```bash
flask --app hadith_app run
```

Direct execution from `server/` is also supported:

```bash
python hadith_app/app.py
```

Both commands use the same registered Flask application. The production entrypoint
remains `gunicorn hadith_app:app`.

The app should now be running on `http://127.0.0.1:5000/`. You can visit this URL in your web browser to view the daily
Hadith.

## Data Sources

This project utilizes Hadith collections from reliable and authentic sources, including:

- Sahih Bukhari
- Sahih Muslim
- Sunan Abu Dawood
- And other major Hadith collections

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Create a new Pull Request.

Please ensure your code follows the project's coding standards and includes tests for any new functionality.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.