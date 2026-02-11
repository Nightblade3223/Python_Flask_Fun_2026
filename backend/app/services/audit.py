from flask import g

from app.extensions import db
from app.models import AuditLog


def log_event(event_type: str, target_type: str, target_id=None, actor_user_id=None, details=None):
    log = AuditLog(
        actor_user_id=actor_user_id,
        event_type=event_type,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        details=details or {},
        request_id=getattr(g, "request_id", None),
    )
    db.session.add(log)
    db.session.commit()
