import pytest

from app import create_app
from app.extensions import db, bcrypt
from app.models import Group, Permission, User


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        perms = ["users.read", "users.write", "groups.read", "groups.write", "admin.panel", "audit.read"]
        perm_objs = []
        for p in perms:
            obj = Permission(name=p)
            db.session.add(obj)
            perm_objs.append(obj)
        admin_group = Group(name="Admin")
        admin_group.permissions = perm_objs
        default_group = Group(name="Default")
        db.session.add_all([admin_group, default_group])
        admin = User(email="admin@example.com", password_hash=bcrypt.generate_password_hash("admin123!").decode(), is_email_verified=True)
        viewer = User(email="viewer@example.com", password_hash=bcrypt.generate_password_hash("viewer123!").decode(), is_email_verified=True)
        admin.groups.append(admin_group)
        viewer.groups.append(default_group)
        db.session.add_all([admin, viewer])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, email, password):
    resp = client.post('/api/auth/login', json={"email": email, "password": password})
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
