from flask import Blueprint, jsonify, request, g

from app.extensions import bcrypt, db
from app.models import AuditLog, Group, Permission, User
from app.schemas.payloads import (
    GroupCreateSchema,
    GroupMemberChangeSchema,
    GroupPatchSchema,
    GroupPermChangeSchema,
    UserCreateSchema,
    UserPatchSchema,
    validate,
)
from app.services.audit import log_event
from app.utils.decorators import require_perm
from app.utils.errors import error_response

api_bp = Blueprint("api", __name__, url_prefix="/api")


def user_payload(user):
    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified,
        "must_reset_password": user.must_reset_password,
        "group_ids": [g.id for g in user.groups],
        "permissions": user.permissions(),
    }


def group_payload(group):
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "members": [{"id": u.id, "email": u.email} for u in group.users],
        "permissions": [p.name for p in group.permissions],
    }


@api_bp.get("/users")
@require_perm("users.read")
def users_list():
    return jsonify({"items": [user_payload(user) for user in User.query.order_by(User.id).all()]})


@api_bp.post("/users")
@require_perm("users.write")
def users_create():
    data = validate(UserCreateSchema(), request.get_json(silent=True) or {})
    if isinstance(data, dict) and "email" not in data:
        return error_response("VALIDATION_ERROR", "Invalid request", 400, data)
    if User.query.filter_by(email=data["email"].lower()).first():
        return error_response("CONFLICT", "Email already exists", 409)
    user = User(email=data["email"].lower(), password_hash=bcrypt.generate_password_hash(data["password"]).decode())
    groups = Group.query.filter(Group.id.in_(data["group_ids"])).all() if data["group_ids"] else []
    user.groups = groups
    db.session.add(user)
    db.session.commit()
    log_event("user.created", "user", target_id=user.id, actor_user_id=g.current_user.id)
    return jsonify(user_payload(user)), 201


@api_bp.get("/users/<int:user_id>")
@require_perm("users.read")
def users_get(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user_payload(user))


@api_bp.patch("/users/<int:user_id>")
@require_perm("users.write")
def users_patch(user_id):
    user = User.query.get_or_404(user_id)
    data = validate(UserPatchSchema(), request.get_json(silent=True) or {})
    if isinstance(data, dict) and not any(k in ["email", "is_active", "must_reset_password"] for k in data.keys()):
        return error_response("VALIDATION_ERROR", "Invalid request", 400, data)
    if "email" in data:
        user.email = data["email"].lower()
    if "is_active" in data:
        user.is_active = data["is_active"]
    if "must_reset_password" in data:
        user.must_reset_password = data["must_reset_password"]
    db.session.commit()
    log_event("user.updated", "user", target_id=user.id, actor_user_id=g.current_user.id, details=data)
    return jsonify(user_payload(user))


@api_bp.get("/groups")
@require_perm("groups.read")
def groups_list():
    return jsonify({"items": [group_payload(group) for group in Group.query.order_by(Group.id).all()]})


@api_bp.post("/groups")
@require_perm("groups.write")
def groups_create():
    data = validate(GroupCreateSchema(), request.get_json(silent=True) or {})
    if isinstance(data, dict) and "name" not in data:
        return error_response("VALIDATION_ERROR", "Invalid request", 400, data)
    group = Group(name=data["name"], description=data.get("description", ""))
    db.session.add(group)
    db.session.commit()
    log_event("group.created", "group", target_id=group.id, actor_user_id=g.current_user.id)
    return jsonify(group_payload(group)), 201


@api_bp.patch("/groups/<int:group_id>")
@require_perm("groups.write")
def groups_patch(group_id):
    group = Group.query.get_or_404(group_id)
    data = validate(GroupPatchSchema(), request.get_json(silent=True) or {})
    if isinstance(data, dict) and not any(k in ["name", "description"] for k in data.keys()):
        return error_response("VALIDATION_ERROR", "Invalid request", 400, data)
    for key in ["name", "description"]:
        if key in data:
            setattr(group, key, data[key])
    db.session.commit()
    log_event("group.updated", "group", target_id=group.id, actor_user_id=g.current_user.id, details=data)
    return jsonify(group_payload(group))


@api_bp.post("/groups/<int:group_id>/members")
@require_perm("groups.write")
def groups_members(group_id):
    group = Group.query.get_or_404(group_id)
    data = validate(GroupMemberChangeSchema(), request.get_json(silent=True) or {})
    if isinstance(data, dict) and "user_id" not in data:
        return error_response("VALIDATION_ERROR", "Invalid request", 400, data)
    user = User.query.get_or_404(data["user_id"])
    if data["action"] == "add" and user not in group.users:
        group.users.append(user)
    elif data["action"] == "remove" and user in group.users:
        group.users.remove(user)
    else:
        return error_response("VALIDATION_ERROR", "action must be add/remove", 400)
    db.session.commit()
    log_event("group.membership_changed", "group", target_id=group.id, actor_user_id=g.current_user.id, details=data)
    return jsonify(group_payload(group))


@api_bp.post("/groups/<int:group_id>/perms")
@require_perm("groups.write")
def groups_permissions(group_id):
    group = Group.query.get_or_404(group_id)
    data = validate(GroupPermChangeSchema(), request.get_json(silent=True) or {})
    if isinstance(data, dict) and "permission" not in data:
        return error_response("VALIDATION_ERROR", "Invalid request", 400, data)
    perm = Permission.query.filter_by(name=data["permission"]).first()
    if not perm:
        perm = Permission(name=data["permission"])
        db.session.add(perm)
        db.session.flush()
    if data["action"] == "add" and perm not in group.permissions:
        group.permissions.append(perm)
    elif data["action"] == "remove" and perm in group.permissions:
        group.permissions.remove(perm)
    else:
        return error_response("VALIDATION_ERROR", "action must be add/remove", 400)
    db.session.commit()
    log_event("group.permission_changed", "group", target_id=group.id, actor_user_id=g.current_user.id, details=data)
    return jsonify(group_payload(group))


@api_bp.get("/audit")
@require_perm("audit.read")
def audit_list():
    rows = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return jsonify({"items": [{
        "id": r.id,
        "event_type": r.event_type,
        "target_type": r.target_type,
        "target_id": r.target_id,
        "details": r.details,
        "request_id": r.request_id,
        "created_at": r.created_at.isoformat(),
    } for r in rows]})
