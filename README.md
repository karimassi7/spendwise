# SpendWise

SpendWise is a web-based personal finance application written in Python with Flask.
It helps multiple users organize their finances while keeping every profile's
records separate and secure behind email/password authentication.

## Features

- Secure sign up / sign in with password hashing and per-user data isolation.
- Manage accounts (cash / bank / savings) and track total balances.
- Record income and expenses with search, filters, and sorting.
- Create spending categories (income / expense).
- Create budgets per category and monitor spending progress.
- Create savings goals and record contributions.
- Dashboard with monthly income-vs-expense charts (Chart.js), budget progress,
  savings progress, and recent transactions.
- Update your profile (name, currency, monthly income) and change your password.
- Store application data in MySQL with foreign-key protection.
- Delete a profile together with only the financial data it owns.

## Architecture

The application packages live directly under `src` and are organized into clear
layers:

- `domain`: Financial classes and validation rules.
- `repositories`: MySQL persistence and data retrieval.
- `database`: Connection settings, schema initialization.
- `service`: Business rules and profile-scoped operations.
- `webapp`: Flask application factory, controllers, templates, and static assets.
- `tests`: Automated tests for domain rules and web flows.

## Run the Application

Create a virtual environment and install the project from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Then run the application with either entry point:

```powershell
python run.py
python -m webapp
spendwise
```

Open http://127.0.0.1:5000 in your browser and create an account.

## Configuration

Create a `.env` file at the repository root (or rely on the defaults):

```
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=spendwise
FLASK_SECRET_KEY=change-me
FLASK_DEBUG=0
```

## Database Setup

Initialize the database after installing the project:

```powershell
python -m database.setup_database
```

The default connection is `root` with an empty password on
`127.0.0.1:3306`. Override it with the `MYSQL_*` environment variables above.