# Flask Modern Boilerplate

A Flask starter project with:

- User system (signup, login, signout)
- Admin panel
- Modern UI powered by **Vue 3** on top of Flask templates
- `pytest` tests
- `gunicorn` for production serving

## Project structure

```text
app/
  admin/routes.py
  auth/routes.py
  main/routes.py
  templates/
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

## Run with gunicorn

```bash
gunicorn -w 3 -b 0.0.0.0:8000 run:app
```

Open http://127.0.0.1:8000

## Run tests

```bash
pytest -q
```
