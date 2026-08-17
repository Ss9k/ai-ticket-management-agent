"""
Admin routes.
GET  /admin                    — admin dashboard
GET  /admin/engineers/pending  — pending engineers
POST /admin/engineers/approve  — approve engineer
GET  /admin/tickets            — all tickets
POST /admin/assign             — assign engineer
"""
import logging
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify

from frontend.services.api_client import APIClient

bp = Blueprint("admin", __name__, url_prefix="/admin")
logger = logging.getLogger(__name__)


def _require_admin():
    if "user_id" not in session or session.get("role") != "admin":
        return False
    return True


@bp.route("/")
def dashboard():
    if not _require_admin():
        flash("Admin access required.", "danger")
        return redirect(url_for("auth.login"))

    admin_id = session["user_id"]

    # Load pending engineers
    eng_resp = APIClient.get_pending_engineers(admin_id)
    pending_engineers = eng_resp.data if eng_resp.ok and isinstance(eng_resp.data, list) else []

    # Load all tickets
    ticket_resp = APIClient.get_all_tickets(admin_id)
    tickets = ticket_resp.data if ticket_resp.ok and isinstance(ticket_resp.data, list) else []

    # Load approved engineers for assignment dropdown
    approved_resp = APIClient.get_approved_engineers(admin_id)
    approved_engineers = approved_resp.data if approved_resp.ok and isinstance(approved_resp.data, list) else []

    return render_template(
        "admin/dashboard.html",
        pending_engineers=pending_engineers,
        tickets=tickets,
        approved_engineers=approved_engineers,
    )


@bp.route("/engineers/approve", methods=["POST"])
def approve_engineer():
    if not _require_admin():
        flash("Admin access required.", "danger")
        return redirect(url_for("auth.login"))

    engineer_id = request.form.get("engineer_id")
    if not engineer_id:
        flash("Engineer ID missing.", "danger")
        return redirect(url_for("admin.dashboard"))

    resp = APIClient.approve_engineer(int(engineer_id), session["user_id"])
    if resp.ok:
        flash("Engineer approved successfully.", "success")
    else:
        flash(resp.error or "Failed to approve engineer.", "danger")

    return redirect(url_for("admin.dashboard"))


@bp.route("/assign", methods=["POST"])
def assign_engineer():
    if not _require_admin():
        flash("Admin access required.", "danger")
        return redirect(url_for("auth.login"))

    ticket_id = request.form.get("ticket_id")
    engineer_id = request.form.get("engineer_id")

    if not ticket_id or not engineer_id:
        flash("Ticket ID and engineer are required.", "danger")
        return redirect(url_for("admin.dashboard"))

    resp = APIClient.assign_engineer(int(ticket_id), int(engineer_id), session["user_id"])
    if resp.ok:
        flash("Ticket assigned successfully.", "success")
    else:
        flash(resp.error or "Failed to assign engineer.", "danger")

    return redirect(url_for("admin.dashboard"))
