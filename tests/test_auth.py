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
