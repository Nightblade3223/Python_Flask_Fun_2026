from app.extensions import db
from app.models import Group, User


def create_admin_and_login(client, app):
    with app.app_context():
        admin = User(username="admin", email="admin@example.com", is_admin=True)
        admin.set_password("password123")
        user = User(username="member", email="member@example.com", is_admin=False)
        user.set_password("password123")
        db.session.add_all([admin, user])
        db.session.commit()
        return admin.id, user.id


def test_group_crud_and_user_update(client, app):
    admin_id, user_id = create_admin_and_login(client, app)
    login = client.post("/api/login", json={"email": "admin@example.com", "password": "password123"})
    assert login.status_code == 200

    create_group = client.post("/admin/api/groups", json={"name": "Editors", "permissions": "posts.read, posts.write"})
    assert create_group.status_code == 200

    with app.app_context():
        group = Group.query.filter_by(name="Editors").first()
        assert group is not None
        group_id = group.id
        assert group.permissions == "posts.read,posts.write"

    update_user = client.post(
        f"/admin/api/users/{user_id}",
        json={
            "username": "member-updated",
            "email": "member-updated@example.com",
            "is_admin": False,
            "group_ids": [group_id],
        },
    )
    assert update_user.status_code == 200

    with app.app_context():
        user = db.session.get(User, user_id)
        assert user.username == "member-updated"
        assert user.email == "member-updated@example.com"
        assert [group.name for group in user.groups] == ["Editors"]

    update_group = client.post(f"/admin/api/groups/{group_id}", json={"name": "Moderators", "permissions": "users.read"})
    assert update_group.status_code == 200

    with app.app_context():
        group = db.session.get(Group, group_id)
        assert group.name == "Moderators"
        assert group.permissions == "users.read"

    delete_group = client.post(f"/admin/api/groups/{group_id}/delete")
    assert delete_group.status_code == 200

    delete_user = client.post(f"/admin/api/users/{user_id}/delete")
    assert delete_user.status_code == 200

    with app.app_context():
        assert db.session.get(User, user_id) is None
        assert db.session.get(Group, group_id) is None
        assert db.session.get(User, admin_id) is not None


def test_admin_safety_rules(client, app):
    admin_id, _ = create_admin_and_login(client, app)
    client.post("/api/login", json={"email": "admin@example.com", "password": "password123"})

    demote_self = client.post(
        f"/admin/api/users/{admin_id}",
        json={"username": "admin", "email": "admin@example.com", "is_admin": False, "group_ids": []},
    )
    assert demote_self.status_code == 400

    delete_self = client.post(f"/admin/api/users/{admin_id}/delete")
    assert delete_self.status_code == 400
