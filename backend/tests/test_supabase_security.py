import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app
from backend.app.database import engine, SessionLocal
from backend.app.models.appointment import Appointment
from backend.app.models.payment import Payment
from backend.app.models.user import User, Patient, Doctor

app.state.limiter.enabled = False
client = TestClient(app)

def get_auth_token(email: str, password: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def auth_tokens():
    tokens = {
        "patient": get_auth_token("smit.gamit@demo.caresync.local", "Patient@12345"),
        "doctor": get_auth_token("aarav.mehta@demo.caresync.local", "Doctor@12345"),
        "admin": get_auth_token("admin@demo.caresync.local", "Admin@12345"),
    }
    return tokens

# ============================================================================
# 1. DATABASE RLS & PRIVILEGES VERIFICATION (PostgreSQL)
# ============================================================================

def test_rls_enabled_on_all_public_tables():
    """Verify that RLS is enabled for all 9 tables in the public schema."""
    if engine.name != "postgresql":
        pytest.skip("RLS catalog test applies to PostgreSQL only")

    with engine.connect() as conn:
        query = """
        SELECT c.relname, c.relrowsecurity
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' 
          AND c.relkind = 'r'
          AND c.relname IN (
            'users', 'doctors', 'patients', 'doctor_availabilities',
            'appointments', 'payments', 'notifications',
            'feedback_ratings', 'password_resets'
          );
        """
        rows = conn.execute(text(query)).fetchall()
        table_rls = {r[0]: r[1] for r in rows}

        expected_tables = [
            "users", "doctors", "patients", "doctor_availabilities",
            "appointments", "payments", "notifications",
            "feedback_ratings", "password_resets"
        ]

        for table in expected_tables:
            assert table in table_rls, f"Table {table} not found in public schema"
            assert table_rls[table] is True, f"RLS is NOT enabled on table: {table}"

def test_no_sensitive_columns_exposed_to_anon_or_authenticated():
    """Verify that anon and authenticated roles have NO SELECT access to sensitive columns."""
    if engine.name != "postgresql":
        pytest.skip("Catalog privileges test applies to PostgreSQL only")

    with engine.connect() as conn:
        query = """
        SELECT DISTINCT c.table_name, c.column_name, g.grantee
        FROM information_schema.columns c
        JOIN information_schema.role_table_grants g 
          ON g.table_name = c.table_name AND g.table_schema = c.table_schema
        WHERE c.table_schema = 'public'
          AND g.grantee IN ('anon', 'authenticated')
          AND g.privilege_type = 'SELECT'
          AND (
              c.column_name ILIKE '%password%' OR
              c.column_name ILIKE '%token%' OR
              c.column_name ILIKE '%secret%' OR
              c.column_name ILIKE '%key%' OR
              c.column_name ILIKE '%hash%' OR
              c.column_name ILIKE '%medical%' OR
              c.column_name ILIKE '%reason%' OR
              c.column_name ILIKE '%comment%' OR
              c.column_name ILIKE '%payment%' OR
              c.column_name ILIKE '%transaction%' OR
              c.column_name ILIKE '%receipt%'
          );
        """
        rows = conn.execute(text(query)).fetchall()
        assert len(rows) == 0, f"Sensitive columns still exposed to anon/authenticated: {rows}"

# ============================================================================
# 2. APPLICATION-LEVEL ROLE & OWNERSHIP AUTHORIZATION
# ============================================================================

def test_unauthenticated_requests_blocked():
    """Endpoints requiring authentication must reject requests without tokens."""
    res = client.get("/api/appointments/patient/history")
    assert res.status_code == 401

    res = client.get("/api/patients/me")
    assert res.status_code == 401

    res = client.get("/api/notifications")
    assert res.status_code == 401

def test_patient_cannot_access_other_patient_record(auth_tokens):
    """Patient cannot access another patient's medical records via ID."""
    db = SessionLocal()
    try:
        # Find a patient that doesn't belong to the logged-in user
        logged_in_user = db.query(User).filter(User.email == "smit.gamit@demo.caresync.local").first()
        other_patient = db.query(Patient).filter(Patient.user_id != logged_in_user.id).first()
        
        if other_patient:
            res = client.get(
                f"/api/patients/{other_patient.id}",
                headers={"Authorization": f"Bearer {auth_tokens['patient']}"}
            )
            assert res.status_code == 403, f"Expected 403 Forbidden, got {res.status_code}: {res.text}"
    finally:
        db.close()

def test_patient_cannot_view_other_patient_receipt(auth_tokens):
    """Patient cannot view a receipt for an appointment they do not own."""
    db = SessionLocal()
    try:
        logged_in_user = db.query(User).filter(User.email == "smit.gamit@demo.caresync.local").first()
        other_payment = db.query(Payment).join(Patient).filter(Patient.user_id != logged_in_user.id).first()
        
        if other_payment:
            res = client.get(
                f"/api/payments/receipt/{other_payment.receipt_number}",
                headers={"Authorization": f"Bearer {auth_tokens['patient']}"}
            )
            assert res.status_code == 403, f"Expected 403 Forbidden, got {res.status_code}: {res.text}"
    finally:
        db.close()

def test_doctor_public_listing_accessible():
    """Public doctor listing and specialization search must remain functional without auth."""
    res = client.get("/api/doctors")
    assert res.status_code == 200
    docs = res.json()
    assert isinstance(docs, list)
    assert len(docs) > 0

    res = client.get("/api/doctors/specializations")
    assert res.status_code == 200
    assert "Cardiologist" in res.json()
