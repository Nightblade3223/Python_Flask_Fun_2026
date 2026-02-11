from datetime import datetime, timedelta, timezone
import secrets

from flask import Blueprint, current_app, g, jsonify, request

from app.extensions import bcrypt, db, limiter
from app.models import EmailVerificationToken, PasswordResetToken, User
from app.schemas.payloads import LoginSchema, RequestPasswordResetSchema, ResetPasswordSchema, VerifyTokenSchema, validate
from app.services.audit import log_event
from app.utils.auth import make_jwt
from app.utils.decorators import require_auth
from app.utils.errors import error_response


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _public_user_payload(user):
    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified,
        "must_reset_password": user.must_reset_password,
        "permissions": user.permissions(),
    }


@auth_bp.post("/login")
@limiter.limit("5/minute")
def login():
    data = validate(LoginSchema(), request.get_json(silent=True) or {})
    if isinstance(data, dict) and "email" not in data:
        return error_response("VALIDATION_ERROR", "Invalid request", 400, data)

    user = User.query.filter_by(email=data["email"].lower()).first()
    now = datetime.now(timezone.utc)
    if not user:
        log_event("login.failure", "user", details={"email": data["email"]})
        return error_response("INVALID_CREDENTIALS", "Invalid email or password", 401)
    if user.locked_until and user.locked_until > now:
        return error_response("ACCOUNT_LOCKED", "Account temporarily locked", 423)
    if not bcrypt.check_password_hash(user.password_hash, data["password"]):
        user.failed_logins += 1
        if user.failed_logins >= 5:
            user.locked_until = now + timedelta(minutes=15)
            user.failed_logins = 0
        db.session.commit()
        log_event("login.failure", "user", target_id=user.id, actor_user_id=user.id)
        return error_response("INVALID_CREDENTIALS", "Invalid email or password", 401)

    user.failed_logins = 0
    user.locked_until = None
    db.session.commit()
    token = make_jwt(user.id, remember_me=data.get("remember_me", False))
    log_event("login.success", "user", target_id=user.id, actor_user_id=user.id)
    return jsonify({"token": token, "user": _public_user_payload(user)})


@auth_bp.post("/logout")
def logout():
    return jsonify({"ok": True})


@auth_bp.get("/me")
@require_auth
def me():
    return jsonify({"user": _public_user_payload(g.current_user)})


@auth_bp.post("/request-password-reset")
@limiter.limit("5/hour")
def request_password_reset():
    data = validate(RequestPasswordResetSchema(), request.get_json(silent=True) or {})
    if isinstance(data, dict) and "email" not in data:
        return error_response("VALIDATION_ERROR", "Invalid request", 400, data)
    user = User.query.filter_by(email=data["email"].lower()).first()
    if user:
        token = secrets.token_urlsafe(32)
        rec = PasswordResetToken(user_id=user.id, token=token, expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
        db.session.add(rec)
        db.session.commit()
        print(f"[dev-email] Password reset link: {current_app.config['FRONTEND_ORIGIN']}/reset-password?token={token}")
        log_event("password_reset.requested", "user", target_id=user.id, actor_user_id=user.id)
    return jsonify({"ok": True})


@auth_bp.post("/reset-password")
@limiter.limit("10/hour")
def reset_password():
    data = validate(ResetPasswordSchema(), request.get_json(silent=True) or {})
    if isinstance(data, dict) and "token" not in data:
        return error_response("VALIDATION_ERROR", "Invalid request", 400, data)
    rec = PasswordResetToken.query.filter_by(token=data["token"]).first()
    if not rec or rec.used_at is not None or rec.expires_at < datetime.now(timezone.utc):
        return error_response("TOKEN_INVALID", "Reset token is invalid", 400)
    user = User.query.get(rec.user_id)
    user.password_hash = bcrypt.generate_password_hash(data["new_password"]).decode()
    user.must_reset_password = False
    rec.used_at = datetime.now(timezone.utc)
    db.session.commit()
    log_event("password_reset.completed", "user", target_id=user.id, actor_user_id=user.id)
    return jsonify({"ok": True})


@auth_bp.post("/request-email-verify")
@require_auth
def request_email_verify():
    token = secrets.token_urlsafe(32)
    rec = EmailVerificationToken(user_id=g.current_user.id, token=token, expires_at=datetime.now(timezone.utc) + timedelta(hours=24))
    db.session.add(rec)
    db.session.commit()
    print(f"[dev-email] Email verify link: {current_app.config['FRONTEND_ORIGIN']}/verify-email?token={token}")
    return jsonify({"ok": True})


@auth_bp.post("/verify-email")
def verify_email():
    data = validate(VerifyTokenSchema(), request.get_json(silent=True) or {})
    if isinstance(data, dict) and "token" not in data:
        return error_response("VALIDATION_ERROR", "Invalid request", 400, data)
    rec = EmailVerificationToken.query.filter_by(token=data["token"]).first()
    if not rec or rec.used_at is not None or rec.expires_at < datetime.now(timezone.utc):
        return error_response("TOKEN_INVALID", "Verify token is invalid", 400)
    user = User.query.get(rec.user_id)
    user.is_email_verified = True
    rec.used_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"ok": True})
