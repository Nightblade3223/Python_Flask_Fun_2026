from datetime import datetime, timedelta, timezone
import uuid

import jwt
from flask import current_app, g, request

from app.models import User


def make_jwt(user_id: int, remember_me: bool = False):
    now = datetime.now(timezone.utc)
    ttl = timedelta(days=current_app.config["JWT_REMEMBER_DAYS"]) if remember_me else timedelta(minutes=current_app.config["JWT_EXPIRE_MINUTES"])
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_jwt(token: str):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


def current_user_from_request():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    try:
        payload = decode_jwt(token)
    except jwt.PyJWTError:
        return None
    return User.query.get(int(payload["sub"]))


def ensure_request_id():
    rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    g.request_id = rid
    return rid
