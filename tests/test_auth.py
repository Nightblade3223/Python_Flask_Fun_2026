from app.extensions import db
from app.models import User


def test_signup_makes_first_user_admin(client):
    res = client.post(
        "/api/signup",
        json={"username": "admin", "email": "admin@example.com", "password": "password123"},
    )
    assert res.status_code == 200
    assert res.get_json()["is_admin"] is True


def test_login_and_admin_access(client, app):
    with app.app_context():
        user = User(username="demo", email="demo@example.com", is_admin=True)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    login = client.post("/api/login", json={"email": "demo@example.com", "password": "password123"})
    assert login.status_code == 200

    admin_page = client.get("/admin/")
    assert admin_page.status_code == 200


def test_non_admin_forbidden(client, app):
    with app.app_context():
        user = User(username="demo", email="demo@example.com", is_admin=False)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    client.post("/api/login", json={"email": "demo@example.com", "password": "password123"})
    admin_page = client.get("/admin/")
    assert admin_page.status_code == 403


def test_public_boilerplate_pages(client):
    assert client.get("/").status_code == 200
    assert client.get("/docs").status_code == 200
    assert client.get("/components").status_code == 200


def test_dashboard_requires_login(client, app):
    no_login = client.get("/dashboard")
    assert no_login.status_code in (301, 302)

    with app.app_context():
        user = User(username="member", email="member@example.com", is_admin=False)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    login = client.post("/api/login", json={"email": "member@example.com", "password": "password123"})
    assert login.status_code == 200
    assert client.get("/dashboard").status_code == 200
