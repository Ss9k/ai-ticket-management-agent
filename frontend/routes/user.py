"""
User routes.
GET  /user        — unified dashboard with AI problem input + tickets
POST /user/ask-ai — AJAX endpoint
POST /user/create-ticket — AJAX endpoint
"""
import logging
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify

from frontend.services.api_client import APIClient

bp = Blueprint("user", __name__, url_prefix="/user")
logger = logging.getLogger(__name__)


def _require_user():
    if "user_id" not in session or session.get("role") not in ("user", "admin"):
        return False
    return True


@bp.route("/")
def dashboard():
    if not _require_user():
        flash("Please log in to access the user dashboard.", "warning")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    resp = APIClient.get_user_tickets(user_id)
    tickets = resp.data if resp.ok and isinstance(resp.data, list) else []

    return render_template("user/dashboard.html", tickets=tickets)


@bp.route("/ask-ai", methods=["POST"])
def ask_ai():
    """AJAX: Ask the AI for a solution."""
    if not _require_user():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True) or {}
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()

    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400

    resp = APIClient.ask_ai(
        user_id=session["user_id"],
        title=title,
        description=description,
    )

    if resp.ok:
        return jsonify({"success": True, "response": resp.data})
    else:
        return jsonify({"error": resp.error or "AI service unavailable"}), resp.status_code


@bp.route("/create-ticket", methods=["POST"])
def create_ticket():
    """AJAX: Create a ticket when AI didn't solve the problem."""
    if not _require_user():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True) or {}
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    ai_solution = data.get("ai_solution", "")

    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400

    resp = APIClient.create_ticket(
        user_id=session["user_id"],
        title=title,
        description=description,
        ai_solution=ai_solution,
    )

    if resp.ok:
        return jsonify({"success": True, "ticket": resp.data, "message": "Ticket created successfully."})
    else:
        return jsonify({"error": resp.error or "Failed to create ticket"}), resp.status_code
