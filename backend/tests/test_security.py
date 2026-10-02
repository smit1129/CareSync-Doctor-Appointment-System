import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app

app.state.limiter.enabled = False
client = TestClient(app)

def test_rbac_patient_cannot_access_admin_stats():
    """Verify that a patient cannot access admin-only endpoints (403 Forbidden)."""
    login_res = client.post("/api/auth/login", json={
        "email": "john.doe@gmail.com",
        "password": "Patient@12345"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to access admin stats
    res = client.get("/api/admin/stats", headers=headers)
    assert res.status_code == 403

def test_rbac_doctor_cannot_delete_another_doctor():
    """Verify that a doctor cannot delete another doctor profile (403 Forbidden)."""
    login_res = client.post("/api/auth/login", json={
        "email": "sarah.jenkins@hospital.com",
        "password": "Doctor@12345"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to delete doctor
    res = client.delete("/api/admin/doctors/doc-02", headers=headers)
    assert res.status_code == 403

def test_unauthenticated_request_rejected():
    """Verify that accessing protected endpoints without token returns 401 Unauthorized."""
    res = client.get("/api/appointments/patient/history")
    assert res.status_code == 401

def test_tampered_jwt_token_rejected():
    """Verify that a tampered JWT token returns 401 Unauthorized."""
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tampered.signature"}
    res = client.get("/api/appointments/patient/history", headers=headers)
    assert res.status_code == 401
