"""
Analytics and reports routes (admin only).
GET /analytics
GET /reports
"""
import logging
from flask import Blueprint, render_template, session, redirect, url_for, flash

from frontend.services.api_client import APIClient

bp = Blueprint("analytics", __name__)
logger = logging.getLogger(__name__)


def _require_admin():
    if "user_id" not in session or session.get("role") != "admin":
        return False
    return True


@bp.route("/analytics")
def analytics():
    if not _require_admin():
        flash("Admin access required.", "danger")
        return redirect(url_for("auth.login"))

    resp = APIClient.get_analytics(session["user_id"])
    if resp.ok and isinstance(resp.data, dict):
        data = resp.data
        # Ensure all required keys exist
        if "status_counts" not in data:
            data["status_counts"] = {"pending": 0, "escalated": 0, "resolved": 0, "closed": 0, "total": 0}
        if "category_counts" not in data:
            data["category_counts"] = []
        if "priority_counts" not in data:
            data["priority_counts"] = []
        if "resolution_trends" not in data:
            data["resolution_trends"] = []
        if "engineer_performance" not in data:
            data["engineer_performance"] = []
    else:
        flash(resp.error or "Failed to load analytics.", "danger")
        data = _empty_analytics()

    return render_template("analytics/dashboard.html", data=data)


@bp.route("/reports")
def reports():
    if not _require_admin():
        flash("Admin access required.", "danger")
        return redirect(url_for("auth.login"))

    resp = APIClient.get_reports(session["user_id"])
    if resp.ok and isinstance(resp.data, dict):
        data = resp.data
        # Ensure all required keys exist
        if "status_counts" not in data:
            data["status_counts"] = {"pending": 0, "escalated": 0, "resolved": 0, "closed": 0, "total": 0}
        if "category_counts" not in data:
            data["category_counts"] = []
        if "priority_counts" not in data:
            data["priority_counts"] = []
        if "resolution_trends" not in data:
            data["resolution_trends"] = []
        if "engineer_performance" not in data:
            data["engineer_performance"] = []
    else:
        flash(resp.error or "Failed to load reports.", "danger")
        data = _empty_analytics()

    return render_template("reports/dashboard.html", data=data)


def _empty_analytics():
    return {
        "status_counts": {"pending": 0, "escalated": 0, "resolved": 0, "closed": 0, "total": 0},
        "category_counts": [],
        "priority_counts": [],
        "resolution_trends": [],
        "engineer_performance": [],
    }
