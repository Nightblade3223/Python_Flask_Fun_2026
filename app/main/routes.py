from datetime import date

from flask import Blueprint, render_template
from flask_login import current_user, login_required


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    features = [
        {"title": "Authentication", "description": "Signup/login flow with secure password hashing."},
        {"title": "Blueprint Structure", "description": "Split routes by domain for maintainable growth."},
        {"title": "Admin Controls", "description": "First user becomes admin and can manage users."},
        {"title": "Modern UI", "description": "Styled template system with reusable card widgets."},
    ]

    quick_links = [
        {"label": "Component Library", "endpoint": "main.components"},
        {"label": "Boilerplate Pages", "endpoint": "main.docs"},
        {"label": "Admin Dashboard", "endpoint": "admin.admin_dashboard"},
    ]

    return render_template(
        "index.html",
        user=current_user,
        features=features,
        quick_links=quick_links,
        release_year=date.today().year,
    )


@main_bp.get("/docs")
def docs():
    setup_steps = [
        "Create and activate a Python virtual environment.",
        "Install dependencies from requirements.txt.",
        "Run `python run.py` and open localhost:5000.",
        "Create your first account to become the administrator.",
    ]

    recipe_cards = [
        {
            "title": "Add a new blueprint",
            "description": "Create `app/<module>/routes.py`, register it in `create_app`, and add templates.",
        },
        {
            "title": "Build a JSON API",
            "description": "Use `request.get_json()` + `jsonify()` to create frontend-ready endpoints.",
        },
        {
            "title": "Protect views",
            "description": "Use `@login_required` and role checks for private sections.",
        },
    ]

    return render_template("docs.html", setup_steps=setup_steps, recipe_cards=recipe_cards)


@main_bp.get("/components")
def components():
    metrics = [
        {"label": "Reusable widgets", "value": "8"},
        {"label": "Sample pages", "value": "3"},
        {"label": "Auth endpoints", "value": "2"},
        {"label": "Current version", "value": "v1.0"},
    ]
    return render_template("components.html", metrics=metrics)


@main_bp.get("/dashboard")
@login_required
def dashboard():
    stats = {
        "projects": 4,
        "open_tasks": 13,
        "deployments": 9,
        "uptime": "99.95%",
    }
    timeline = [
        "Initialized Flask app factory and extensions.",
        "Added auth APIs for login and signup.",
        "Created admin panel and role checks.",
        "Expanded starter pages with component examples.",
    ]
    return render_template("dashboard.html", stats=stats, timeline=timeline)
