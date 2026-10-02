import os
import sys
import pytest
import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app
from backend.app.database import init_db, SessionLocal, Base, engine
from backend.seed_data import seed_database
from backend.app.models.appointment import Appointment
from backend.app.models.payment import Payment

app.state.limiter.enabled = False
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    init_db()
    db = SessionLocal()
    seed_database(db)
    db.close()
    yield

state = {}

def get_auth_token(email, password):
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]

def register_patient(email, name, password="Password@123"):
    res = client.post("/api/auth/register", json={
        "name": name,
        "email": email,
        "phone": "+1-555-9000",
        "password": password,
        "role": "patient"
    })
    return res.json()

def test_setup_state():
    state["p1_token"] = get_auth_token("john.doe@gmail.com", "Patient@12345")
    register_patient("patient2@test.com", "Patient Two")
    state["p2_token"] = get_auth_token("patient2@test.com", "Password@123")
    state["admin_token"] = get_auth_token("admin@hospital.com", "Admin@12345")
    state["doc_token"] = get_auth_token("sarah.jenkins@hospital.com", "Doctor@12345")
    
    docs = client.get("/api/doctors", params={"specialization": "Cardiologist"}).json()
    state["doctor_id"] = docs[0]["id"]

# ============================================================================
# 1. PAYMENT RECEIPT — AUTHENTICATION + OWNERSHIP
# ============================================================================

def test_payment_receipt_auth_ownership():
    db = SessionLocal()
    payment = db.query(Payment).first()
    apt = payment.appointment
    rec_num = payment.receipt_number
    
    # Identify which patient owns this appointment
    patient_user_email = apt.patient.user.email
    # Create another patient
    unique_email = f"intruder_{uuid.uuid4().hex[:4]}@test.com"
    register_patient(unique_email, "Intruder")
    intruder_token = get_auth_token(unique_email, "Password@123")
    owner_token = get_auth_token(patient_user_email, "Patient@12345")
    
    # unauthenticated receipt -> 401
    res = client.get(f"/api/payments/receipt/{rec_num}")
    assert res.status_code == 401
    
    # patient own receipt -> success
    res = client.get(f"/api/payments/receipt/{rec_num}", headers={"Authorization": f"Bearer {owner_token}"})
    assert res.status_code == 200
    assert res.json()["receipt_number"] == rec_num
    
    # patient another patient's receipt -> 403
    res = client.get(f"/api/payments/receipt/{rec_num}", headers={"Authorization": f"Bearer {intruder_token}"})
    assert res.status_code == 403
    
    # admin receipt access -> success
    res = client.get(f"/api/payments/receipt/{rec_num}", headers={"Authorization": f"Bearer {state['admin_token']}"})
    assert res.status_code == 200
    
    db.close()

# ============================================================================
# 2. REMOVE CLIENT-CONTROLLED APPOINTMENT STATUS
# ============================================================================

def test_client_cannot_control_initial_status():
    target_date = date.today() + timedelta(days=1)
    while target_date.weekday() != 1:  # Tuesday for Dr. Sarah Jenkins
        target_date += timedelta(days=1)
        
    slots_res = client.get(f"/api/doctors/{state['doctor_id']}/slots", params={"target_date": str(target_date)})
    free_slots = [s for s in slots_res.json() if s["is_available"]]
    assert free_slots
    slot = free_slots[0]["start_time"]
    
    payload = {
        "doctor_id": state["doctor_id"],
        "appointment_date": str(target_date),
        "start_time": slot,
        "reason": "Test status override",
        "initial_status": "Completed"  # Malicious attempt
    }
    res = client.post("/api/appointments/book", json=payload, headers={"Authorization": f"Bearer {state['p1_token']}"})
    
    assert res.status_code == 201
    apt = res.json()
    assert apt["status"] == "Requested", f"Status should be Requested, got {apt['status']}"

# ============================================================================
# 3. ENFORCE DOCTOR AVAILABILITY DURING BOOKING
# ============================================================================

def test_doctor_availability_during_booking():
    # 1. valid available slot -> success (covered by previous test)
    
    target_date = date.today() + timedelta(days=1)
    while target_date.weekday() != 1:  # Tuesday is available (15:00-19:00, 30 min slots)
        target_date += timedelta(days=1)
        
    # Set known schedule for test: Tuesday 15:00 - 19:00
    res = client.post("/api/doctors/me/availability", json=[{
        "day_of_week": 1,
        "start_time": "15:00",
        "end_time": "19:00",
        "slot_duration_minutes": 30,
        "is_active": True
    }], headers={"Authorization": f"Bearer {state['doc_token']}"})
    
    # 2. before availability -> rejected
    res = client.post("/api/appointments/book", json={
        "doctor_id": state["doctor_id"],
        "appointment_date": str(target_date),
        "start_time": "14:30"
    }, headers={"Authorization": f"Bearer {state['p1_token']}"})
    assert res.status_code in [400, 409], "Should reject booking before availability"
    
    # 3. after availability -> rejected
    res = client.post("/api/appointments/book", json={
        "doctor_id": state["doctor_id"],
        "appointment_date": str(target_date),
        "start_time": "19:00"
    }, headers={"Authorization": f"Bearer {state['p1_token']}"})
    assert res.status_code in [400, 409], "Should reject booking after availability"
    
    # 4. appointment crossing availability end -> rejected
    res = client.post("/api/appointments/book", json={
        "doctor_id": state["doctor_id"],
        "appointment_date": str(target_date),
        "start_time": "18:45" # Not a valid slot anyway, but definitely crosses 19:00
    }, headers={"Authorization": f"Bearer {state['p1_token']}"})
    assert res.status_code in [400, 409], "Should reject booking crossing availability end"
    
    # 5. unavailable day -> rejected
    bad_date = target_date + timedelta(days=1) # Wednesday
    res = client.post("/api/appointments/book", json={
        "doctor_id": state["doctor_id"],
        "appointment_date": str(bad_date),
        "start_time": "15:00"
    }, headers={"Authorization": f"Bearer {state['p1_token']}"})
    assert res.status_code in [400, 409], "Should reject booking on unavailable day"

    # 6. already booked slot -> rejected
    res = client.post("/api/appointments/book", json={
        "doctor_id": state["doctor_id"],
        "appointment_date": str(target_date),
        "start_time": "15:00"
    }, headers={"Authorization": f"Bearer {state['p1_token']}"})
    assert res.status_code == 201
    
    res = client.post("/api/appointments/book", json={
        "doctor_id": state["doctor_id"],
        "appointment_date": str(target_date),
        "start_time": "15:00"
    }, headers={"Authorization": f"Bearer {state['p2_token']}"})
    assert res.status_code == 409, "Should reject double booking"

# ============================================================================
# 4. FEEDBACK ONLY AFTER COMPLETED APPOINTMENT
# ============================================================================

def test_feedback_only_after_completed():
    db = SessionLocal()
    apt = db.query(Appointment).first()
    apt_id = apt.id
    
    # Test all statuses except Completed
    for status in ["Requested", "Payment Pending", "Confirmed", "Cancelled", "Rejected", "Rescheduled"]:
        apt.status = status
        db.commit()
        
        # Patient of this appointment
        patient_email = apt.patient.user.email
        pat_token = get_auth_token(patient_email, "Patient@12345")
        
        res = client.post("/api/feedback", json={
            "appointment_id": apt_id,
            "rating": 5,
            "comment": "Great!"
        }, headers={"Authorization": f"Bearer {pat_token}"})
        
        assert res.status_code == 400
        assert "completed" in res.json()["detail"].lower()
        
    # Test Completed
    apt.status = "Completed"
    db.commit()
    
    # Should succeed
    res = client.post("/api/feedback", json={
        "appointment_id": apt_id,
        "rating": 5,
        "comment": "Great!"
    }, headers={"Authorization": f"Bearer {pat_token}"})
    
    assert res.status_code == 201
    
    db.close()

# ============================================================================
# 5. REFUND ENDPOINT AUTHORIZATION
# ============================================================================

def test_refund_authorization():
    db = SessionLocal()
    payment = db.query(Payment).first()
    pay_id = payment.id
    apt = payment.appointment
    patient_email = apt.patient.user.email
    
    owner_token = get_auth_token(patient_email, "Patient@12345")
    
    unique_email = f"intruder_{uuid.uuid4().hex[:4]}@test.com"
    register_patient(unique_email, "Intruder")
    intruder_token = get_auth_token(unique_email, "Password@123")
    
    admin_token = state["admin_token"]
    doc_token = state["doc_token"]

    # 1. unauthenticated refund -> 401
    res = client.post(f"/api/payments/{pay_id}/refund", json={"reason": "test"})
    assert res.status_code == 401

    # 2. doctor attempting refund -> 403
    res = client.post(f"/api/payments/{pay_id}/refund", json={"reason": "test"}, headers={"Authorization": f"Bearer {doc_token}"})
    assert res.status_code == 403

    # 3. patient refunding another patient's payment -> 403
    res = client.post(f"/api/payments/{pay_id}/refund", json={"reason": "test"}, headers={"Authorization": f"Bearer {intruder_token}"})
    assert res.status_code == 403

    # 4. admin refunding any payment -> allowed (200 or 400 depending on if it's already refunded)
    res = client.post(f"/api/payments/{pay_id}/refund", json={"reason": "test"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code in [200, 400] # 400 if already refunded

    # 5. patient refunding own payment -> allowed
    # (Just asserting it doesn't give 401/403, might give 400 if already refunded by admin above)
    res = client.post(f"/api/payments/{pay_id}/refund", json={"reason": "test"}, headers={"Authorization": f"Bearer {owner_token}"})
    assert res.status_code not in [401, 403]
    
    db.close()
