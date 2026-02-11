# Flask Modern Boilerplate

A more built-out Flask starter project with:

- User system (signup, login, signout)
- Admin panel
- Example authenticated dashboard page
- Boilerplate docs page and widget/component showcase page
- Modern UI powered by **Vue 3** on top of Flask templates
- `pytest` tests
- `gunicorn` for production serving

## Frameworks and tooling used

- **Flask** (web framework)
- **Jinja2** (templating engine used by Flask)
- **Flask-SQLAlchemy** (ORM and database integration)
- **Flask-Login** (session auth and user management)
- **Vue 3** (frontend interactivity for auth forms)
- **pytest** (test runner)
- **gunicorn** (production WSGI server)

## Project structure

```text
app/
  admin/routes.py
  auth/routes.py
  main/routes.py
  templates/
    base.html
    index.html
    docs.html
    components.html
    dashboard.html
  static/css/app.css
tests/
run.py
requirements.txt
```

## Setup and run

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Flask dev server:

```bash
python run.py
```

Open http://127.0.0.1:5000

> The **first account created** becomes an admin automatically.

## Included example pages

- `/` Home starter page with feature cards and quick links
- `/docs` Boilerplate setup and recipe page
- `/components` Widget/component examples page
- `/dashboard` Authenticated sample dashboard page
- `/admin/` Admin user listing page

## Run with gunicorn

```bash
gunicorn -w 3 -b 0.0.0.0:8000 run:app
```

Open http://127.0.0.1:8000

## Run tests

```bash
pytest -q
```
