from functools import wraps

from flask import g

from app.utils.auth import current_user_from_request
from app.utils.errors import error_response


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user_from_request()
        if not user or not user.is_active:
            return error_response("UNAUTHORIZED", "Authentication required", 401)
        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


def require_perm(permission):
    def decorator(fn):
        @wraps(fn)
        @require_auth
        def wrapper(*args, **kwargs):
            user = g.current_user
            if permission not in user.permissions():
                return error_response("FORBIDDEN", "You do not have required permission", 403, {"required": permission})
            return fn(*args, **kwargs)

        return wrapper

    return decorator
