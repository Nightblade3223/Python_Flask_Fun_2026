from flask import Blueprint, abort, jsonify, render_template, request
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Group, User


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _ensure_admin() -> None:
    if not current_user.is_admin:
        abort(403)


def _parse_permissions(raw_permissions: str) -> str:
    entries = [entry.strip() for entry in raw_permissions.split(",") if entry.strip()]
    return ",".join(dict.fromkeys(entries))


@admin_bp.get("/")
@login_required
def admin_dashboard():
    _ensure_admin()

    users = User.query.order_by(User.id.asc()).all()
    groups = Group.query.order_by(Group.name.asc()).all()
    return render_template("admin.html", users=users, groups=groups)


@admin_bp.post("/api/users/<int:user_id>")
@login_required
def update_user(user_id: int):
    _ensure_admin()

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    is_admin = bool(payload.get("is_admin", False))
    group_ids = payload.get("group_ids") or []

    if len(username) < 3 or "@" not in email:
        return jsonify({"error": "Please provide valid username and email."}), 400

    existing = User.query.filter(User.id != user.id, (User.username == username) | (User.email == email)).first()
    if existing:
        return jsonify({"error": "Username or email already in use."}), 409

    if user.id == current_user.id and not is_admin:
        return jsonify({"error": "You cannot remove your own admin access."}), 400

    valid_group_ids = [gid for gid in group_ids if isinstance(gid, int)]
    groups = Group.query.filter(Group.id.in_(valid_group_ids)).all() if valid_group_ids else []

    user.username = username
    user.email = email
    user.is_admin = is_admin
    user.groups = groups
    db.session.commit()
    return jsonify({"ok": True})


@admin_bp.post("/api/users/<int:user_id>/delete")
@login_required
def delete_user(user_id: int):
    _ensure_admin()

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    if user.id == current_user.id:
        return jsonify({"error": "You cannot delete your own account."}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({"ok": True})


@admin_bp.post("/api/groups")
@login_required
def create_group():
    _ensure_admin()

    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    permissions = _parse_permissions(payload.get("permissions") or "")

    if len(name) < 2:
        return jsonify({"error": "Group name must be at least 2 characters."}), 400

    if Group.query.filter_by(name=name).first():
        return jsonify({"error": "A group with this name already exists."}), 409

    group = Group(name=name, permissions=permissions)
    db.session.add(group)
    db.session.commit()
    return jsonify({"ok": True})


@admin_bp.post("/api/groups/<int:group_id>")
@login_required
def update_group(group_id: int):
    _ensure_admin()

    group = db.session.get(Group, group_id)
    if not group:
        return jsonify({"error": "Group not found."}), 404

    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    permissions = _parse_permissions(payload.get("permissions") or "")

    if len(name) < 2:
        return jsonify({"error": "Group name must be at least 2 characters."}), 400

    existing = Group.query.filter(Group.id != group.id, Group.name == name).first()
    if existing:
        return jsonify({"error": "A group with this name already exists."}), 409

    group.name = name
    group.permissions = permissions
    db.session.commit()
    return jsonify({"ok": True})


@admin_bp.post("/api/groups/<int:group_id>/delete")
@login_required
def delete_group(group_id: int):
    _ensure_admin()

    group = db.session.get(Group, group_id)
    if not group:
        return jsonify({"error": "Group not found."}), 404

    db.session.delete(group)
    db.session.commit()
    return jsonify({"ok": True})
