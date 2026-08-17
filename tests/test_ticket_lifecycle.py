"""
Tests: Full ticket lifecycle — create, assign, resolve, close, analytics
"""
import pytest
from werkzeug.security import generate_password_hash
from backend.models.user import User, UserRole, UserStatus
from backend.models.ticket import Ticket, TicketStatus


def _create_admin(db):
    u = User(name="Admin", email="admin@t.com",
             password=generate_password_hash("pw"), role=UserRole.admin, status=UserStatus.approved)
    db.add(u); db.commit(); db.refresh(u); return u


def _create_user(db, email="user@t.com"):
    u = User(name="User", email=email,
             password=generate_password_hash("pw"), role=UserRole.user, status=UserStatus.approved)
    db.add(u); db.commit(); db.refresh(u); return u


def _create_engineer(db, email="eng@t.com", approved=True):
    u = User(name="Eng", email=email, password=generate_password_hash("pw"),
             role=UserRole.engineer,
             status=UserStatus.approved if approved else UserStatus.pending)
    db.add(u); db.commit(); db.refresh(u); return u


class TestTicketCreation:
    def test_create_ticket(self, client, db):
        user = _create_user(db)
        r = client.post("/user/create-ticket", json={
            "user_id": user.id, "title": "VPN broken", "description": "Cannot connect to VPN"
        })
        assert r.status_code == 201
        data = r.json()
        assert data["status"] == "pending"
        assert data["title"] == "VPN broken"

    def test_create_ticket_requires_existing_user(self, client, db):
        r = client.post("/user/create-ticket", json={
            "user_id": 9999, "title": "X", "description": "Y"
        })
        assert r.status_code == 404


class TestTicketAssignment:
    def test_admin_can_assign_engineer(self, client, db):
        admin = _create_admin(db)
        user = _create_user(db)
        engineer = _create_engineer(db)

        tr = client.post("/user/create-ticket", json={
            "user_id": user.id, "title": "VPN issue", "description": "Cannot connect"
        })
        ticket_id = tr.json()["id"]

        ar = client.post("/admin/assign", json={
            "ticket_id": ticket_id, "engineer_id": engineer.id, "admin_id": admin.id
        })
        assert ar.status_code == 200
        assert ar.json()["status"] == "escalated"

    def test_non_admin_cannot_assign(self, client, db):
        user = _create_user(db)
        engineer = _create_engineer(db)

        tr = client.post("/user/create-ticket", json={
            "user_id": user.id, "title": "X", "description": "Y"
        })
        ticket_id = tr.json()["id"]

        ar = client.post("/admin/assign", json={
            "ticket_id": ticket_id, "engineer_id": engineer.id, "admin_id": user.id
        })
        assert ar.status_code == 403


class TestEngineerAccess:
    def test_engineer_can_view_assigned_ticket(self, client, db):
        admin = _create_admin(db)
        user = _create_user(db)
        engineer = _create_engineer(db)

        tr = client.post("/user/create-ticket", json={
            "user_id": user.id, "title": "Test", "description": "Desc"
        })
        ticket_id = tr.json()["id"]
        client.post("/admin/assign", json={
            "ticket_id": ticket_id, "engineer_id": engineer.id, "admin_id": admin.id
        })

        dr = client.get(f"/engineer/tickets/{ticket_id}?engineer_id={engineer.id}")
        assert dr.status_code == 200
        assert dr.json()["id"] == ticket_id

    def test_engineer_cannot_view_unassigned_ticket(self, client, db):
        user = _create_user(db)
        eng1 = _create_engineer(db, "e1@t.com")
        eng2 = _create_engineer(db, "e2@t.com")
        admin = _create_admin(db)

        tr = client.post("/user/create-ticket", json={
            "user_id": user.id, "title": "T", "description": "D"
        })
        ticket_id = tr.json()["id"]
        client.post("/admin/assign", json={
            "ticket_id": ticket_id, "engineer_id": eng1.id, "admin_id": admin.id
        })

        # eng2 should not be able to access this ticket
        dr = client.get(f"/engineer/tickets/{ticket_id}?engineer_id={eng2.id}")
        assert dr.status_code == 403

    def test_pending_engineer_blocked(self, client, db):
        pending_eng = _create_engineer(db, approved=False)
        dr = client.get(f"/engineer/tickets?engineer_id={pending_eng.id}")
        assert dr.status_code == 403


class TestTicketResolution:
    def _setup(self, client, db):
        admin = _create_admin(db)
        user = _create_user(db)
        engineer = _create_engineer(db)

        tr = client.post("/user/create-ticket", json={
            "user_id": user.id, "title": "VPN down", "description": "Error 691"
        })
        ticket_id = tr.json()["id"]
        client.post("/admin/assign", json={
            "ticket_id": ticket_id, "engineer_id": engineer.id, "admin_id": admin.id
        })
        return ticket_id, engineer, admin

    def test_engineer_resolves_ticket(self, client, db):
        ticket_id, engineer, _ = self._setup(client, db)
        r = client.post(f"/engineer/tickets/{ticket_id}/resolve", json={
            "engineer_id": engineer.id,
            "resolution_notes": "Reset VPN credentials and cleared MFA cache.",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "resolved"

    def test_resolve_updates_history(self, client, db):
        ticket_id, engineer, _ = self._setup(client, db)
        client.post(f"/engineer/tickets/{ticket_id}/resolve", json={
            "engineer_id": engineer.id,
            "resolution_notes": "Fixed it.",
        })
        hr = client.get(f"/engineer/tickets/{ticket_id}/history?engineer_id={engineer.id}")
        assert hr.status_code == 200
        history = hr.json()
        statuses = [h["new_status"] for h in history]
        assert "resolved" in statuses

    def test_close_resolved_ticket(self, client, db):
        ticket_id, engineer, _ = self._setup(client, db)
        client.post(f"/engineer/tickets/{ticket_id}/resolve", json={
            "engineer_id": engineer.id, "resolution_notes": "Done."
        })
        cr = client.post(f"/engineer/tickets/{ticket_id}/close", json={
            "closed_by_id": engineer.id
        })
        assert cr.status_code == 200
        assert cr.json()["status"] == "closed"

    def test_cannot_close_pending_ticket(self, client, db):
        ticket_id, engineer, _ = self._setup(client, db)
        cr = client.post(f"/engineer/tickets/{ticket_id}/close", json={
            "closed_by_id": engineer.id
        })
        assert cr.status_code == 400


class TestAnalytics:
    def test_admin_can_access_analytics(self, client, db):
        admin = _create_admin(db)
        r = client.get(f"/analytics/?admin_id={admin.id}")
        assert r.status_code == 200
        data = r.json()
        assert "status_counts" in data
        assert "category_counts" in data
        assert "engineer_performance" in data

    def test_non_admin_blocked_from_analytics(self, client, db):
        user = _create_user(db)
        r = client.get(f"/analytics/?admin_id={user.id}")
        assert r.status_code == 403

    def test_analytics_reflect_ticket_states(self, client, db):
        admin = _create_admin(db)
        user = _create_user(db)
        engineer = _create_engineer(db)

        # Create and resolve a ticket
        tr = client.post("/user/create-ticket", json={
            "user_id": user.id, "title": "T", "description": "D"
        })
        ticket_id = tr.json()["id"]
        client.post("/admin/assign", json={
            "ticket_id": ticket_id, "engineer_id": engineer.id, "admin_id": admin.id
        })
        client.post(f"/engineer/tickets/{ticket_id}/resolve", json={
            "engineer_id": engineer.id, "resolution_notes": "Fixed."
        })

        ar = client.get(f"/analytics/?admin_id={admin.id}")
        data = ar.json()
        assert data["status_counts"]["resolved"] >= 1
