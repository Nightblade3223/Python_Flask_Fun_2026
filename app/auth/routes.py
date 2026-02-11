from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    return render_template("login.html")


@auth_bp.get("/signup")
def signup_page():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    return render_template("signup.html")


@auth_bp.post("/api/signup")
def signup_api():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if len(username) < 3 or "@" not in email or len(password) < 8:
        return jsonify({"error": "Please provide valid credentials."}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "User already exists."}), 409

    is_first_user = User.query.count() == 0

    user = User(username=username, email=email, is_admin=is_first_user)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({"ok": True, "is_admin": user.is_admin})


@auth_bp.post("/api/login")
def login_api():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401

    login_user(user)
    return jsonify({"ok": True, "is_admin": user.is_admin})


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
