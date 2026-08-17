"""
Tests: Authentication — register, login, RBAC
"""
import pytest
from fastapi.testclient import TestClient


def register_user(client, name, email, password, role="user"):
    return client.post("/auth/register", json={"name": name, "email": email, "password": password, "role": role})


def login_user(client, email, password):
    return client.post("/auth/login", json={"email": email, "password": password})


class TestRegistration:
    def test_register_user_success(self, client):
        r = register_user(client, "Alice", "alice@test.com", "pass123")
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == "alice@test.com"
        assert data["role"] == "user"
        assert data["status"] == "approved"

    def test_register_engineer_pending(self, client):
        r = register_user(client, "Bob", "bob@test.com", "pass123", "engineer")
        assert r.status_code == 201
        data = r.json()
        assert data["role"] == "engineer"
        assert data["status"] == "pending"

    def test_register_duplicate_email(self, client):
        register_user(client, "Alice", "alice@test.com", "pass123")
        r = register_user(client, "Alice2", "alice@test.com", "pass456")
        assert r.status_code == 400

    def test_register_invalid_role(self, client):
        r = register_user(client, "Admin", "admin@test.com", "pass", "admin")
        assert r.status_code == 422  # Validation error


class TestLogin:
    def test_login_success(self, client):
        register_user(client, "Alice", "alice@test.com", "pass123")
        r = login_user(client, "alice@test.com", "pass123")
        assert r.status_code == 200
        data = r.json()
        assert data["message"] == "Login successful"
        assert data["user"]["email"] == "alice@test.com"

    def test_login_wrong_password(self, client):
        register_user(client, "Alice", "alice@test.com", "pass123")
        r = login_user(client, "alice@test.com", "wrongpass")
        assert r.status_code == 401

    def test_login_unknown_email(self, client):
        r = login_user(client, "nobody@test.com", "pass")
        assert r.status_code == 401

    def test_pending_engineer_cannot_login(self, client):
        register_user(client, "Bob", "bob@test.com", "pass123", "engineer")
        r = login_user(client, "bob@test.com", "pass123")
        assert r.status_code == 401
        assert "pending" in r.json()["detail"].lower()


class TestEngineerApproval:
    def _create_admin(self, db):
        from werkzeug.security import generate_password_hash
        from backend.models.user import User, UserRole, UserStatus
        admin = User(
            name="Admin", email="admin@test.com",
            password=generate_password_hash("admin123"),
            role=UserRole.admin, status=UserStatus.approved
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    def test_approve_engineer(self, client, db):
        admin = self._create_admin(db)
        r = register_user(client, "Bob", "bob@test.com", "pass123", "engineer")
        eng_id = r.json()["id"]

        ar = client.post(f"/admin/engineers/approve?engineer_id={eng_id}&admin_id={admin.id}")
        assert ar.status_code == 200

        # Engineer can now login
        lr = login_user(client, "bob@test.com", "pass123")
        assert lr.status_code == 200

    def test_non_admin_cannot_approve(self, client, db):
        register_user(client, "Bob", "bob@test.com", "pass123", "engineer")
        r2 = register_user(client, "Carol", "carol@test.com", "pass123", "user")
        carol_id = r2.json()["id"]
        eng_r = client.post("/auth/register", json={"name":"Eng","email":"eng2@test.com","password":"p","role":"engineer"})
        eng_id = eng_r.json()["id"]

        ar = client.post(f"/admin/engineers/approve?engineer_id={eng_id}&admin_id={carol_id}")
        assert ar.status_code == 403
