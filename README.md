# Flask + Vue RBAC App (Gunicorn + Postgres)

## Architecture overview
- **Frontend (`frontend/`)**: Vue 3 + Vite + Pinia + Vue Router. Handles login, route guards, and admin pages.
- **Backend (`backend/`)**: Flask app factory (`create_app`) exposing REST endpoints under `/api/*`.
- **Auth**: JWT bearer tokens. Chosen over cookie sessions to avoid CSRF complexity in SPA API calls; token expiry + remember-me TTL are enforced server-side.
- **RBAC**: users belong to many groups, groups contain many permissions. Endpoints are protected via `@require_perm(...)`.
- **Database**: Postgres in Docker Compose (SQLite only in `testing`/local fallback).
- **Server**: Gunicorn only for production paths (`wsgi:app`).

Data flow: browser → Vue API client (`Authorization: Bearer <token>`) → Flask decorators (`require_auth` / `require_perm`) → SQLAlchemy models → JSON response.

## Database schema
- `users`: login identity, active/verified flags, lockout counters.
- `groups`: RBAC groups.
- `permissions`: atomic permission strings (e.g., `users.write`).
- `group_members` (M2M): user ↔ group.
- `group_permissions` (M2M): group ↔ permission.
- `password_reset_tokens`: reset flow tokens + expiry.
- `email_verification_tokens`: email verify tokens + expiry.
- `audit_logs`: security and admin events with request IDs.

Indexes: `users.email`, `permissions.name`, token fields, audit `event_type` and `request_id`.

## Permissions model
- Permissions are plain strings stored in `permissions`.
- Groups aggregate permissions; users aggregate from all groups.
- Endpoint checks are server-side on every protected route via `@require_perm("...")`.
- Example permissions seeded: `users.read`, `users.write`, `groups.read`, `groups.write`, `admin.panel`, `audit.read`.

## Repo layout
```text
backend/
  app/
    __init__.py
    api/routes.py
    auth/routes.py
    models/__init__.py
    schemas/payloads.py
    services/audit.py
    utils/
  migrations/versions/
  tests/
  wsgi.py
  Dockerfile
frontend/
  src/
    api/client.js
    router/index.js
    stores/auth.js
    views/
  Dockerfile
docker-compose.yml
README.md
```

## Implementation plan (what was implemented)
1. Build Flask app factory + extensions + models.
2. Implement JWT auth + login throttling + reset/verify flows.
3. Implement RBAC decorators and admin APIs for users/groups/perms.
4. Add audit logging + structured security/error responses.
5. Add Alembic migration script.
6. Build Vue SPA login/admin UI with route guards and Pinia session store.
7. Add Docker/Compose with Postgres + Gunicorn + Vite frontend.
8. Add pytest tests for auth and permission behavior.

## API endpoints (implemented)
- Auth: `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`, `POST /api/auth/request-password-reset`, `POST /api/auth/reset-password`, `POST /api/auth/request-email-verify`, `POST /api/auth/verify-email`
- Users: `GET /api/users`, `POST /api/users`, `GET /api/users/<id>`, `PATCH /api/users/<id>`
- Groups: `GET /api/groups`, `POST /api/groups`, `PATCH /api/groups/<id>`, `POST /api/groups/<id>/members`, `POST /api/groups/<id>/perms`
- Audit: `GET /api/audit`

Error shape:
```json
{ "error": { "code": "SOME_CODE", "message": "Human message", "details": {} } }
```

## Local setup
### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=manage.py
export DATABASE_URL=sqlite:///dev.db
flask db upgrade
flask seed
gunicorn -w 2 -b 0.0.0.0:8000 --access-logfile - --error-logfile - "wsgi:app"
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Docker (recommended)
```bash
docker compose up --build
```

App URLs:
- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`

## Bootstrap admin user
```bash
docker compose exec backend flask bootstrap-admin
```
(or locally: `cd backend && flask bootstrap-admin`)

## Migrations workflow
```bash
cd backend
export FLASK_APP=manage.py
flask db upgrade
# For new changes:
flask db migrate -m "message"
flask db upgrade
```

## Security notes
- JWT auth with expiration + remember-me TTL.
- Rate limiting on auth endpoints (`Flask-Limiter`).
- Password hashing via bcrypt.
- Request IDs on responses and audit rows.
- Security headers (`nosniff`, `DENY` frame, `Referrer-Policy`).
- Server-side permission enforcement on protected endpoints.

## Seed data
`flask seed` creates:
- `Admin` group with all default permissions.
- `Default` group with minimal permissions.

## Test plan
- Auth login happy-path.
- Permission denial for user lacking admin permission.
- Group permission assignment changes effective permissions.

Run:
```bash
cd backend
pytest -q
```
