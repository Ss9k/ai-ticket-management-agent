"""
Engineer routes.
GET  /engineer                         — dashboard
GET  /engineer/tickets                 — open tickets list
GET  /engineer/tickets/<id>            — ticket detail
POST /engineer/tickets/<id>/remarks    — add remarks
POST /engineer/tickets/<id>/resolve    — resolve ticket
POST /engineer/tickets/<id>/close      — close ticket
"""
import logging
from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from frontend.services.api_client import APIClient

bp = Blueprint("engineer", __name__, url_prefix="/engineer")
logger = logging.getLogger(__name__)


def _require_engineer():
    if "user_id" not in session or session.get("role") != "engineer":
        return False
    return True


@bp.route("/")
def dashboard():
    if not _require_engineer():
        flash("Engineer access required.", "danger")
        return redirect(url_for("auth.login"))

    resp = APIClient.get_engineer_dashboard(session["user_id"])
    if not resp.ok:
        flash(resp.error or "Failed to load dashboard.", "danger")
        dashboard_data = {
            "kpi": {"open": 0, "escalated": 0, "resolved": 0, "closed": 0, "high_priority": 0, "total": 0},
            "priority_counts": {"P1": 0, "P2": 0, "P3": 0, "P4": 0},
            "category_counts": {},
            "recent_activity": [],
            "engineer_name": session.get("user_name", "Engineer"),
        }
    else:
        dashboard_data = resp.data
        # Ensure all required keys exist with defaults
        if "kpi" not in dashboard_data:
            dashboard_data["kpi"] = {"open": 0, "escalated": 0, "resolved": 0, "closed": 0, "high_priority": 0, "total": 0}
        if "priority_counts" not in dashboard_data:
            dashboard_data["priority_counts"] = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
        if "category_counts" not in dashboard_data:
            dashboard_data["category_counts"] = {}
        if "recent_activity" not in dashboard_data:
            dashboard_data["recent_activity"] = []
        if "engineer_name" not in dashboard_data:
            dashboard_data["engineer_name"] = session.get("user_name", "Engineer")

    return render_template("engineer/dashboard.html", data=dashboard_data)


@bp.route("/tickets")
def tickets():
    if not _require_engineer():
        flash("Engineer access required.", "danger")
        return redirect(url_for("auth.login"))

    # Filter parameters
    status = request.args.get("status")
    priority = request.args.get("priority")
    category = request.args.get("category")
    severity = request.args.get("severity")
    search = request.args.get("search")

    resp = APIClient.get_engineer_tickets(
        engineer_id=session["user_id"],
        status=status, priority=priority,
        category=category, severity=severity, search=search,
    )
    ticket_list = resp.data if resp.ok and isinstance(resp.data, list) else []

    return render_template(
        "engineer/tickets.html",
        tickets=ticket_list,
        filters={"status": status, "priority": priority, "category": category,
                 "severity": severity, "search": search},
    )


@bp.route("/tickets/<int:ticket_id>")
def ticket_detail(ticket_id: int):
    if not _require_engineer():
        flash("Engineer access required.", "danger")
        return redirect(url_for("auth.login"))

    resp = APIClient.get_ticket_detail(ticket_id, session["user_id"])
    if not resp.ok:
        flash(resp.error or "Ticket not found.", "danger")
        return redirect(url_for("engineer.tickets"))

    ticket = resp.data
    return render_template("engineer/ticket_detail.html", ticket=ticket)


@bp.route("/tickets/<int:ticket_id>/remarks", methods=["POST"])
def add_remarks(ticket_id: int):
    if not _require_engineer():
        flash("Engineer access required.", "danger")
        return redirect(url_for("auth.login"))

    remarks = request.form.get("remarks", "").strip()
    if not remarks:
        flash("Remarks cannot be empty.", "warning")
        return redirect(url_for("engineer.ticket_detail", ticket_id=ticket_id))

    resp = APIClient.add_remarks(ticket_id, session["user_id"], remarks)
    if resp.ok:
        flash("Remarks saved successfully.", "success")
    else:
        flash(resp.error or "Failed to save remarks.", "danger")

    return redirect(url_for("engineer.ticket_detail", ticket_id=ticket_id))


@bp.route("/tickets/<int:ticket_id>/resolve", methods=["POST"])
def resolve_ticket(ticket_id: int):
    if not _require_engineer():
        flash("Engineer access required.", "danger")
        return redirect(url_for("auth.login"))

    resolution_notes = request.form.get("resolution_notes", "").strip()
    engineer_remarks = request.form.get("engineer_remarks", "").strip()

    if not resolution_notes:
        flash("Resolution notes are required.", "warning")
        return redirect(url_for("engineer.ticket_detail", ticket_id=ticket_id))

    resp = APIClient.resolve_ticket(ticket_id, session["user_id"], resolution_notes, engineer_remarks)
    if resp.ok:
        flash("Ticket resolved successfully.", "success")
    else:
        flash(resp.error or "Failed to resolve ticket.", "danger")

    return redirect(url_for("engineer.ticket_detail", ticket_id=ticket_id))


@bp.route("/tickets/<int:ticket_id>/close", methods=["POST"])
def close_ticket(ticket_id: int):
    if not _require_engineer():
        flash("Engineer access required.", "danger")
        return redirect(url_for("auth.login"))

    resp = APIClient.close_ticket(ticket_id, session["user_id"])
    if resp.ok:
        flash("Ticket closed successfully.", "success")
        return redirect(url_for("engineer.tickets"))
    else:
        flash(resp.error or "Failed to close ticket.", "danger")
        return redirect(url_for("engineer.ticket_detail", ticket_id=ticket_id))
