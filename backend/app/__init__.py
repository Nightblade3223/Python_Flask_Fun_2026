import logging

from flask import Flask, jsonify, g

from app.api.routes import api_bp
from app.auth.routes import auth_bp
from app.config import CONFIG_MAP
from app.extensions import bcrypt, cors, db, limiter, migrate
from app.models import Group, Permission, User
from app.utils.auth import ensure_request_id
from app.utils.errors import error_response


DEFAULT_PERMISSIONS = [
    "users.read",
    "users.write",
    "groups.read",
    "groups.write",
    "admin.panel",
    "audit.read",
]


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    cfg = config_name or "development"
    app.config.from_object(CONFIG_MAP[cfg])

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    limiter.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": [app.config["FRONTEND_ORIGIN"]]}})

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    @app.before_request
    def before_request():
        ensure_request_id()

    @app.after_request
    def after_request(resp):
        resp.headers["X-Request-ID"] = getattr(g, "request_id", "")
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "same-origin"
        return resp

    @app.errorhandler(404)
    def not_found(_):
        return error_response("NOT_FOUND", "Resource not found", 404)

    @app.errorhandler(429)
    def too_many(_):
        return error_response("RATE_LIMITED", "Too many requests", 429)

    @app.errorhandler(500)
    def internal(_):
        return error_response("INTERNAL_ERROR", "Unexpected server error", 500)

    @app.route("/healthz")
    def healthz():
        return jsonify({"ok": True})

    @app.cli.command("seed")
    def seed():
        for p in DEFAULT_PERMISSIONS:
            if not Permission.query.filter_by(name=p).first():
                db.session.add(Permission(name=p))
        admin = Group.query.filter_by(name="Admin").first()
        if not admin:
            admin = Group(name="Admin", description="Administrator group")
            db.session.add(admin)
        default = Group.query.filter_by(name="Default").first()
        if not default:
            default = Group(name="Default", description="Default low-privilege group")
            db.session.add(default)
        db.session.flush()
        admin.permissions = Permission.query.all()
        db.session.commit()
        print("Seeded groups and permissions")

    @app.cli.command("bootstrap-admin")
    def bootstrap_admin():
        import getpass

        email = input("Admin email: ").strip().lower()
        password = getpass.getpass("Password: ")
        user = User.query.filter_by(email=email).first()
        admin_group = Group.query.filter_by(name="Admin").first()
        if not admin_group:
            print("Run flask seed first")
            return
        if user:
            user.password_hash = bcrypt.generate_password_hash(password).decode()
        else:
            user = User(email=email, password_hash=bcrypt.generate_password_hash(password).decode(), is_email_verified=True)
            db.session.add(user)
        if admin_group not in user.groups:
            user.groups.append(admin_group)
        db.session.commit()
        print("Admin bootstrapped")

    return app
