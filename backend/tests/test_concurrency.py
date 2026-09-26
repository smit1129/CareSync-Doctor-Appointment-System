import os
import sys
import uuid
import pytest
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app
from backend.app.database import init_db, SessionLocal, Base, engine
from backend.seed_data import seed_database

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    init_db()
    db = SessionLocal()
    seed_database(db)
    db.close()
    yield

def test_concurrent_double_booking_prevention():
    """
    Simulate multiple simultaneous booking requests for the exact same doctor, date, and slot.
    Guarantees concurrency safety: EXACTLY ONE succeeds (201), the rest receive 409 Conflict.
    """
    # 1. Register a fresh unique patient for concurrency test
    unique_email = f"racetest_{uuid.uuid4().hex[:6]}@test.com"
    reg_res = client.post("/api/auth/register", json={
        "name": "Race Tester",
        "email": unique_email,
        "phone": "+1-555-4444",
        "password": "Password@123",
        "role": "patient"
    })
    assert reg_res.status_code == 201

    login_res = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": "Password@123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Pick a doctor and target future slot
    docs = client.get("/api/doctors").json()
    doctor_id = docs[0]["id"]
    target_date = date.today() + timedelta(days=25)
    while target_date.weekday() >= 6:
        target_date += timedelta(days=1)
    target_date_str = str(target_date)
    target_slot = "14:30"

    # 3. Fire 8 simultaneous booking requests
    num_requests = 8
    def attempt_booking(idx):
        # Create separate client to simulate distinct concurrent requests
        c = TestClient(app)
        return c.post("/api/appointments/book", json={
            "doctor_id": doctor_id,
            "appointment_date": target_date_str,
            "start_time": target_slot,
            "reason": f"Concurrent race attempt #{idx}"
        }, headers=headers)

    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        results = list(executor.map(attempt_booking, range(num_requests)))

    status_codes = [r.status_code for r in results]
    success_count = status_codes.count(201)
    conflict_count = status_codes.count(409)

    assert success_count == 1, f"Expected exactly 1 booking to succeed, but got {success_count}. Status codes: {status_codes}"
    assert conflict_count == num_requests - 1, f"Expected {num_requests - 1} conflicts (409), but got {conflict_count}"
