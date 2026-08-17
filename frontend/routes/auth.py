"""
Authentication routes — login, register, logout.
Landing page is the login page.
"""
import logging
from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from frontend.services.api_client import APIClient

bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


@bp.route("/", methods=["GET", "POST"])
def login():
    """Landing page is the login form."""
    if "user_id" in session:
        return _redirect_by_role(session.get("role"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("auth/login.html")

        resp = APIClient.login(email, password)
        if resp.ok and isinstance(resp.data, dict):
            user = resp.data.get("user", {})
            session.clear()
            session["user_id"] = user.get("id")
            session["user_name"] = user.get("name")
            session["email"] = user.get("email")
            session["role"] = user.get("role")
            flash(f"Welcome back, {user.get('name')}!", "success")
            logger.info(f"User logged in: {email}")
            return _redirect_by_role(user.get("role"))
        else:
            flash(resp.error or "Invalid credentials.", "danger")

    return render_template("auth/login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return _redirect_by_role(session.get("role"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "user")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")

        if role not in ("user", "engineer"):
            flash("Invalid role selected.", "danger")
            return render_template("auth/register.html")

        resp = APIClient.register(name, email, password, role)
        if resp.ok:
            if role == "engineer":
                flash("Engineer registration submitted. Your account is pending admin approval.", "info")
            else:
                flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash(resp.error or "Registration failed.", "danger")

    return render_template("auth/register.html")


@bp.route("/logout")
def logout():
    name = session.get("user_name", "")
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


def _redirect_by_role(role: str):
    if role == "admin":
        return redirect(url_for("admin.dashboard"))
    elif role == "engineer":
        return redirect(url_for("engineer.dashboard"))
    else:
        return redirect(url_for("user.dashboard"))
