from conftest import login


def test_login_success(client):
    resp = client.post('/api/auth/login', json={"email": "admin@example.com", "password": "admin123!"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user"]["email"] == "admin@example.com"
    assert "admin.panel" in data["user"]["permissions"]


def test_permission_enforcement(client):
    headers = login(client, "viewer@example.com", "viewer123!")
    resp = client.get('/api/users', headers=headers)
    assert resp.status_code == 403


def test_group_membership_affects_permissions(client, app):
    admin_headers = login(client, "admin@example.com", "admin123!")
    resp = client.post('/api/groups/2/perms', headers=admin_headers, json={"permission": "users.read", "action": "add"})
    assert resp.status_code == 200

    viewer_headers = login(client, "viewer@example.com", "viewer123!")
    ok_resp = client.get('/api/users', headers=viewer_headers)
    assert ok_resp.status_code == 200
