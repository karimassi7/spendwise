# SpendWise

SpendWise is a command-line personal finance application written in Python. It helps multiple users organize their finances while keeping every profile's records separate.

## Features

- Create, select, update, and delete multiple profiles.
- Manage accounts, income, expenses, and spending categories.
- Create budgets and monitor spending progress.
- Create savings goals and record contributions.
- View balances, monthly summaries, and a financial dashboard.
- Store application data in MySQL with foreign-key protection.
- Delete a profile together with only the financial data it owns.

## Architecture

The project is organized into clear layers:

- `domain`: Financial classes and validation rules.
- `repositories`: MySQL persistence and data retrieval.
- `database`: Connection settings, schema initialization.
- `service`: Business rules and profile-scoped operations.
- `presentation`: Command-line menus, formatting, and user interaction.
- `tests`: Automated tests for profile isolation and menu behavior.

## Run the Application

From the directory containing the `spendwise` package, run:

```powershell
python -m spendwise.presentation.main
```

## Database Setup

Install the dependencies and initialize the database from the directory containing
the `spendwise` package:

```powershell
pip install -r spendwise/requirements.txt
python -m spendwise.database.setup_database
```

The default connection is `root` with an empty password on
`127.0.0.1:3306`. Override it with `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`,
`MYSQL_PASSWORD`, and `MYSQL_DATABASE` environment variables.

Create or select a profile before managing accounts, transactions, budgets,
categories, or savings goals.
