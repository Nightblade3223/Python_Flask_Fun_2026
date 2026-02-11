from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required

from ..models import User


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)

    users = User.query.order_by(User.id.asc()).all()
    return render_template("admin.html", users=users)
