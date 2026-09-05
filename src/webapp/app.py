"""Flask application factory for the SpendWise web app."""

import os
from pathlib import Path


def _load_dotenv(path: str) -> None:
    """Load MY_VAR=VALUE lines from a .env file into os.environ if unset."""
    env_path = Path(path)
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def create_app() -> "Flask":
    """Build and configure the Flask application."""
    from flask import Flask

    _load_dotenv(str(Path(__file__).parents[2] / ".env"))
    _load_dotenv(".env")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY"
    )
    app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "0") == "1"

    from webapp.auth import get_current_user
    from webapp.controllers import (
        account_bp,
        auth_bp,
        budget_bp,
        category_bp,
        dashboard_bp,
        goal_bp,
        settings_bp,
        transaction_bp,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(goal_bp)
    app.register_blueprint(settings_bp)

    @app.context_processor
    def inject_globals():
        from datetime import date

        return {"current_user": get_current_user(), "today": date.today()}

    @app.errorhandler(404)
    def not_found(error):
        return render_error(404, "Page not found.")

    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_error(405, "Method not allowed.")

    @app.errorhandler(500)
    def server_error(error):
        return render_error(500, "Something went wrong on our end.")

    return app


def render_error(status: int, message: str):
    from flask import render_template

    return render_template("error.html", status_code=status, message=message), status


def main() -> None:
    """Run the development server (used by the `spendwise` console script)."""
    app = create_app()
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=app.config.get("DEBUG", False),
    )
