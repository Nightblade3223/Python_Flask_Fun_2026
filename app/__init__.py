from flask import Flask

from .extensions import db, login_manager


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev-secret-change-me",
        SQLALCHEMY_DATABASE_URI="sqlite:///app.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    return app
