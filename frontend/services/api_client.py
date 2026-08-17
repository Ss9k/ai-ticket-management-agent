"""
Centralized HTTP client for all frontend → backend API calls.
Never call the backend directly from route handlers — always use this client.
"""
import logging
import requests
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Imported lazily to avoid circular import at module level
_backend_url: Optional[str] = None


def _get_backend_url() -> str:
    global _backend_url
    if _backend_url is None:
        from frontend.config import Config
        _backend_url = Config.BACKEND_URL
    return _backend_url


class APIResponse:
    """Normalized API response wrapper."""

    def __init__(self, ok: bool, data: Any, status_code: int, error: str = ""):
        self.ok = ok
        self.data = data
        self.status_code = status_code
        self.error = error

    def __repr__(self):
        return f"<APIResponse ok={self.ok} status={self.status_code}>"


def _make_request(method: str, path: str, **kwargs) -> APIResponse:
    url = f"{_get_backend_url()}{path}"
    try:
        response = requests.request(method, url, timeout=60, **kwargs)
        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text}

        if response.status_code < 400:
            return APIResponse(ok=True, data=data, status_code=response.status_code)
        else:
            # Extract error message safely
            if isinstance(data, dict):
                error_msg = data.get("detail", data.get("message", str(data)))
            else:
                error_msg = str(data)
            logger.warning(f"API error {response.status_code} at {path}: {error_msg}")
            return APIResponse(ok=False, data=data, status_code=response.status_code, error=error_msg)

    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to backend at {url}")
        return APIResponse(ok=False, data={}, status_code=503, error="Cannot connect to backend service")
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout at {url}")
        return APIResponse(ok=False, data={}, status_code=504, error="Request timed out")
    except Exception as e:
        logger.error(f"Unexpected error calling {url}: {e}")
        return APIResponse(ok=False, data={}, status_code=500, error=str(e))


class APIClient:
    """Static methods for each API call."""

    # --- AUTH ---
    @staticmethod
    def register(name: str, email: str, password: str, role: str = "user") -> APIResponse:
        return _make_request("POST", "/auth/register", json={
            "name": name, "email": email, "password": password, "role": role
        })

    @staticmethod
    def login(email: str, password: str) -> APIResponse:
        return _make_request("POST", "/auth/login", json={"email": email, "password": password})

    # --- USER ---
    @staticmethod
    def ask_ai(user_id: int, title: str, description: str) -> APIResponse:
        return _make_request("POST", "/user/ai", json={
            "user_id": user_id, "title": title, "description": description
        })

    @staticmethod
    def create_ticket(user_id: int, title: str, description: str, ai_solution: str = "") -> APIResponse:
        return _make_request("POST", "/user/create-ticket", json={
            "user_id": user_id, "title": title, "description": description, "ai_solution": ai_solution
        })

    @staticmethod
    def get_user_tickets(user_id: int) -> APIResponse:
        return _make_request("GET", "/user/tickets", params={"user_id": user_id})

    # --- ADMIN ---
    @staticmethod
    def get_pending_engineers(admin_id: int) -> APIResponse:
        return _make_request("GET", "/admin/engineers/pending", params={"admin_id": admin_id})

    @staticmethod
    def approve_engineer(engineer_id: int, admin_id: int) -> APIResponse:
        return _make_request("POST", "/admin/engineers/approve",
                             params={"engineer_id": engineer_id, "admin_id": admin_id})

    @staticmethod
    def get_approved_engineers(admin_id: int) -> APIResponse:
        return _make_request("GET", "/admin/engineers", params={"admin_id": admin_id})

    @staticmethod
    def get_all_tickets(admin_id: int) -> APIResponse:
        return _make_request("GET", "/admin/tickets", params={"admin_id": admin_id})

    @staticmethod
    def assign_engineer(ticket_id: int, engineer_id: int, admin_id: int) -> APIResponse:
        return _make_request("POST", "/admin/assign", json={
            "ticket_id": ticket_id, "engineer_id": engineer_id, "admin_id": admin_id
        })

    # --- ENGINEER ---
    @staticmethod
    def get_engineer_dashboard(engineer_id: int) -> APIResponse:
        resp = _make_request("GET", "/engineer/dashboard", params={"engineer_id": engineer_id})
        # Ensure we always return a valid structure even if backend fails
        if not resp.ok or not isinstance(resp.data, dict):
            return APIResponse(
                ok=False,
                data={
                    "kpi": {"open": 0, "escalated": 0, "resolved": 0, "closed": 0, "high_priority": 0, "total": 0},
                    "priority_counts": {"P1": 0, "P2": 0, "P3": 0, "P4": 0},
                    "category_counts": {},
                    "recent_activity": [],
                    "engineer_name": "Engineer",
                },
                status_code=resp.status_code,
                error=resp.error,
            )
        return resp

    @staticmethod
    def get_engineer_tickets(engineer_id: int, status=None, priority=None,
                              category=None, severity=None, search=None) -> APIResponse:
        params = {"engineer_id": engineer_id}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        if category:
            params["category"] = category
        if severity:
            params["severity"] = severity
        if search:
            params["search"] = search
        return _make_request("GET", "/engineer/tickets", params=params)

    @staticmethod
    def get_ticket_detail(ticket_id: int, engineer_id: int) -> APIResponse:
        return _make_request("GET", f"/engineer/tickets/{ticket_id}", params={"engineer_id": engineer_id})

    @staticmethod
    def add_remarks(ticket_id: int, engineer_id: int, remarks: str) -> APIResponse:
        return _make_request("POST", f"/engineer/tickets/{ticket_id}/remarks",
                             json={"engineer_id": engineer_id, "remarks": remarks})

    @staticmethod
    def resolve_ticket(ticket_id: int, engineer_id: int,
                        resolution_notes: str, engineer_remarks: str = "") -> APIResponse:
        return _make_request("POST", f"/engineer/tickets/{ticket_id}/resolve", json={
            "engineer_id": engineer_id,
            "resolution_notes": resolution_notes,
            "engineer_remarks": engineer_remarks,
        })

    @staticmethod
    def close_ticket(ticket_id: int, closed_by_id: int) -> APIResponse:
        return _make_request("POST", f"/engineer/tickets/{ticket_id}/close",
                             json={"closed_by_id": closed_by_id})

    @staticmethod
    def get_ticket_history(ticket_id: int, engineer_id: int) -> APIResponse:
        return _make_request("GET", f"/engineer/tickets/{ticket_id}/history",
                             params={"engineer_id": engineer_id})

    # --- ANALYTICS ---
    @staticmethod
    def get_analytics(admin_id: int) -> APIResponse:
        logger.info(f"Fetching analytics for admin_id={admin_id}")
        response = _make_request("GET", "/analytics/", params={"admin_id": admin_id})
        logger.info(f"Analytics response: ok={response.ok}, data keys={list(response.data.keys()) if isinstance(response.data, dict) else 'not a dict'}")
        if response.ok and isinstance(response.data, dict):
            logger.info(f"  category_counts: {len(response.data.get('category_counts', []))} items")
            logger.info(f"  priority_counts: {len(response.data.get('priority_counts', []))} items")
            logger.info(f"  resolution_trends: {len(response.data.get('resolution_trends', []))} items")
        return response

    @staticmethod
    def get_reports(admin_id: int) -> APIResponse:
        return _make_request("GET", "/reports/", params={"admin_id": admin_id})

    # --- HEALTH ---
    @staticmethod
    def health() -> APIResponse:
        return _make_request("GET", "/health")
