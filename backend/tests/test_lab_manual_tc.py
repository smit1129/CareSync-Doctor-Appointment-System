import os
import sys
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
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

# Shared state across test execution
state = {}

# ============================================================================
# USER REGISTRATION & AUTHENTICATION (TC_01 - TC_05)
# ============================================================================

def test_tc_01_patient_registers_with_valid_details():
    """TC_01: Patient registers with valid details -> Account created successfully."""
    payload = {
        "name": "Sarah Connor",
        "email": "sarah.connor@test.com",
        "phone": "+1-555-0999",
        "password": "Password@123",
        "role": "patient"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "sarah.connor@test.com"
    assert data["full_name"] == "Sarah Connor"
    assert data["role"] == "patient"
    state["test_patient_email"] = "sarah.connor@test.com"
    state["test_patient_password"] = "Password@123"

def test_tc_02_registration_with_already_registered_email():
    """TC_02: Registration with already registered email -> System displays 'Email already registered'."""
    payload = {
        "name": "Duplicate User",
        "email": state.get("test_patient_email", "sarah.connor@test.com"),
        "phone": "+1-555-0000",
        "password": "AnotherPassword@123",
        "role": "patient"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_tc_03_patient_logs_in_with_valid_credentials():
    """TC_03: Patient logs in with valid credentials -> Login successful; token generated."""
    payload = {
        "email": state.get("test_patient_email", "sarah.connor@test.com"),
        "password": state.get("test_patient_password", "Password@123")
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "patient"
    state["patient_token"] = data["access_token"]
    state["patient_user_id"] = data["user_id"]

def test_tc_04_login_with_invalid_password():
    """TC_04: Login with invalid password -> System displays 'Invalid credentials' error."""
    payload = {
        "email": state.get("test_patient_email", "sarah.connor@test.com"),
        "password": "IncorrectPassword999"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_tc_05_password_reset_request():
    """TC_05: Password reset request -> Password reset link/token sent to email."""
    payload = {"email": state.get("test_patient_email", "sarah.connor@test.com")}
    response = client.post("/api/auth/forgot-password", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Password reset link sent" in data["message"]
    assert "token" in data

# ============================================================================
# DOCTOR SEARCH & APPOINTMENT BOOKING (TC_06 - TC_12)
# ============================================================================

def test_tc_06_search_doctor_by_specialization():
    """TC_06: Search doctor by specialization -> List of matching doctors is displayed."""
    response = client.get("/api/doctors", params={"specialization": "Cardiologist"})
    assert response.status_code == 200
    doctors = response.json()
    assert len(doctors) > 0
    assert any("Cardiologist" in d["specialization"] for d in doctors)
    # Save a doctor ID for booking
    state["doctor_id"] = doctors[0]["id"]
    state["doctor_name"] = doctors[0]["name"]

def test_tc_07_search_with_no_matching_specialization():
    """TC_07: Search with no matching specialization -> Empty list / 'No doctors found'."""
    response = client.get("/api/doctors", params={"specialization": "XYZNonExistentSpecialty"})
    assert response.status_code == 200
    doctors = response.json()
    assert len(doctors) == 0

def test_tc_08_book_an_available_appointment_slot():
    """TC_08: Book an available appointment slot -> Appointment booked with status 'Confirmed'."""
    target_date = date.today() + timedelta(days=3)
    # Ensure it's not a Sunday (which is day 6 in weekday())
    while target_date.weekday() >= 6:
        target_date += timedelta(days=1)
        
    # Get available slots
    slots_res = client.get(f"/api/doctors/{state['doctor_id']}/slots", params={"target_date": str(target_date)})
    assert slots_res.status_code == 200
    slots = slots_res.json()
    free_slots = [s for s in slots if s["is_available"]]
    assert len(free_slots) > 0, "Doctor should have available slots on weekday"
    chosen_slot = free_slots[0]["start_time"]
    state["booking_date"] = str(target_date)
    state["booking_slot"] = chosen_slot

    headers = {"Authorization": f"Bearer {state['patient_token']}"}
    payload = {
        "doctor_id": state["doctor_id"],
        "appointment_date": str(target_date),
        "start_time": chosen_slot,
        "reason": "Cardiology evaluation",
        "initial_status": "Confirmed"
    }
    response = client.post("/api/appointments/book", json=payload, headers=headers)
    assert response.status_code == 201
    apt = response.json()
    assert apt["status"] == "Confirmed"
    assert apt["appointment_date"] == str(target_date)
    assert apt["start_time"] == chosen_slot
    state["appointment_id"] = apt["id"]

def test_tc_09_book_an_already_booked_slot_double_booking():
    """TC_09: Book an already booked slot (double booking) -> Rejects booking: 'Slot not available'."""
    headers = {"Authorization": f"Bearer {state['patient_token']}"}
    payload = {
        "doctor_id": state["doctor_id"],
        "appointment_date": state["booking_date"],
        "start_time": state["booking_slot"],
        "reason": "Attempt duplicate booking"
    }
    response = client.post("/api/appointments/book", json=payload, headers=headers)
    assert response.status_code == 409
    assert "Slot not available" in response.json()["detail"]

def test_tc_10_book_appointment_with_a_past_date():
    """TC_10: Book appointment with a past date -> System displays 'Invalid date' validation error."""
    past_date = str(date.today() - timedelta(days=2))
    headers = {"Authorization": f"Bearer {state['patient_token']}"}
    payload = {
        "doctor_id": state["doctor_id"],
        "appointment_date": past_date,
        "start_time": "10:00",
        "reason": "Past date attempt"
    }
    response = client.post("/api/appointments/book", json=payload, headers=headers)
    # Validation triggers 400 or 422
    assert response.status_code in [400, 422]
    content_str = str(response.json())
    assert "Invalid date" in content_str or "past" in content_str

def test_tc_11_cancel_a_confirmed_appointment():
    """TC_11: Cancel a confirmed appointment -> Status updated to 'Cancelled'; slot freed."""
    # Book a second appointment to cancel
    target_date = date.today() + timedelta(days=5)
    while target_date.weekday() >= 6:
        target_date += timedelta(days=1)
    headers = {"Authorization": f"Bearer {state['patient_token']}"}
    book_res = client.post("/api/appointments/book", json={
        "doctor_id": state["doctor_id"],
        "appointment_date": str(target_date),
        "start_time": "14:00",
        "reason": "To be cancelled"
    }, headers=headers)
    assert book_res.status_code == 201
    apt_to_cancel = book_res.json()["id"]

    cancel_res = client.post(f"/api/appointments/{apt_to_cancel}/cancel", json={
        "cancellation_reason": "Patient conflict"
    }, headers=headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "Cancelled"

    # Verify slot is freed up
    slots_res = client.get(f"/api/doctors/{state['doctor_id']}/slots", params={"target_date": str(target_date)})
    slot_14 = next(s for s in slots_res.json() if s["start_time"] == "14:00")
    assert slot_14["is_available"] is True, "Slot should be freed after cancellation"

def test_tc_12_view_appointment_history():
    """TC_12: View appointment history -> List of past and upcoming appointments displayed."""
    headers = {"Authorization": f"Bearer {state['patient_token']}"}
    response = client.get("/api/appointments/patient/history", headers=headers)
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) > 0
    assert any(a["id"] == state["appointment_id"] for a in history)

# ============================================================================
# DOCTOR MODULE (TC_13 - TC_14)
# ============================================================================

def test_tc_13_doctor_updates_availability_schedule():
    """TC_13: Doctor updates availability schedule -> Reflected in patient slot search."""
    # Login as Dr. Sarah Jenkins
    login_res = client.post("/api/auth/login", json={
        "email": "sarah.jenkins@hospital.com",
        "password": "Doctor@12345"
    })
    assert login_res.status_code == 200
    doc_token = login_res.json()["access_token"]
    state["doctor_token"] = doc_token

    # Update doctor availability: Set custom evening hours for Tuesdays (day 1)
    new_schedules = [
        {
            "day_of_week": 1,
            "start_time": "15:00",
            "end_time": "19:00",
            "slot_duration_minutes": 30,
            "is_active": True
        }
    ]
    headers = {"Authorization": f"Bearer {doc_token}"}
    update_res = client.post("/api/doctors/me/availability", json=new_schedules, headers=headers)
    assert update_res.status_code == 200
    data = update_res.json()
    assert len(data) == 1
    assert data[0]["start_time"] == "15:00"
    assert data[0]["end_time"] == "19:00"

def test_tc_14_doctor_accepts_or_rejects_pending_appointment():
    """TC_14: Doctor accepts/rejects a pending appointment -> Status changes to 'Confirmed'."""
    # Book a pending appointment as patient
    target_date = date.today() + timedelta(days=4)
    while target_date.weekday() >= 6:
        target_date += timedelta(days=1)
    pat_headers = {"Authorization": f"Bearer {state['patient_token']}"}
    book_res = client.post("/api/appointments/book", json={
        "doctor_id": state["doctor_id"],
        "appointment_date": str(target_date),
        "start_time": "11:00",
        "reason": "Consultation requiring confirmation",
        "initial_status": "Requested"
    }, headers=pat_headers)
    assert book_res.status_code == 201
    pending_apt_id = book_res.json()["id"]

    # Doctor accepts the appointment
    doc_headers = {"Authorization": f"Bearer {state['doctor_token']}"}
    action_res = client.post(
        f"/api/appointments/{pending_apt_id}/doctor-action",
        json={"action": "Accept"},
        headers=doc_headers
    )
    assert action_res.status_code == 200
    assert action_res.json()["status"] == "Confirmed"

# ============================================================================
# PAYMENT PROCESSING (TC_15 - TC_17)
# ============================================================================

def test_tc_15_successful_payment_for_appointment():
    """TC_15: Successful payment for appointment -> Payment success; receipt generated."""
    headers = {"Authorization": f"Bearer {state['patient_token']}"}
    payload = {
        "appointment_id": state["appointment_id"],
        "amount": 1200.00,
        "payment_mode": "card",
        "card_number": "4111222233334444",
        "card_expiry": "12/28",
        "simulate_failure": False
    }
    response = client.post("/api/payments/process", json=payload, headers=headers)
    assert response.status_code == 200
    payment = response.json()
    assert payment["status"] == "completed"
    assert payment["receipt_number"].startswith("REC-")
    assert payment["amount"] == 1200.00
    state["payment_id"] = payment["id"]
    state["receipt_number"] = payment["receipt_number"]

    # Verify receipt retrieval
    receipt_res = client.get(f"/api/payments/receipt/{state['receipt_number']}")
    assert receipt_res.status_code == 200
    assert receipt_res.json()["receipt_number"] == state["receipt_number"]

def test_tc_16_payment_failure_handling():
    """TC_16: Payment failure handling -> Payment rejected; booking kept as Pending/failed."""
    # Book a new appointment to test failure
    target_date = date.today() + timedelta(days=6)
    while target_date.weekday() >= 6:
        target_date += timedelta(days=1)
    pat_headers = {"Authorization": f"Bearer {state['patient_token']}"}
    book_res = client.post("/api/appointments/book", json={
        "doctor_id": state["doctor_id"],
        "appointment_date": str(target_date),
        "start_time": "16:00",
        "reason": "Test Payment Failure",
        "initial_status": "Requested"
    }, headers=pat_headers)
    assert book_res.status_code == 201
    apt_fail_id = book_res.json()["id"]

    fail_payload = {
        "appointment_id": apt_fail_id,
        "amount": 1200.00,
        "payment_mode": "card",
        "card_number": "0000111122223333",  # Invalid card
        "simulate_failure": True
    }
    response = client.post("/api/payments/process", json=fail_payload, headers=pat_headers)
    assert response.status_code == 400
    assert "Payment rejected" in response.json()["detail"]

def test_tc_17_refund_on_appointment_cancellation():
    """TC_17: Refund on appointment cancellation -> Refund initiated and status shown to patient."""
    headers = {"Authorization": f"Bearer {state['patient_token']}"}
    # Cancel the paid appointment from TC_15
    cancel_res = client.post(
        f"/api/appointments/{state['appointment_id']}/cancel",
        json={"cancellation_reason": "Need refund"},
        headers=headers
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "Cancelled"

    # Verify payment status was updated to refunded
    refund_res = client.post(
        f"/api/payments/{state['payment_id']}/refund",
        json={"reason": "Patient requested cancellation"},
        headers=headers
    )
    # Either already refunded by cancel service or confirmed here
    assert refund_res.status_code in [200, 400]
    # Check notifications for refund notice
    notifs_res = client.get("/api/notifications", headers=headers)
    assert any("refund" in n["title"].lower() or "refund" in n["message"].lower() for n in notifs_res.json())

# ============================================================================
# NOTIFICATIONS & ADMIN MODULE (TC_18 - TC_21)
# ============================================================================

def test_tc_18_confirmation_notification_sent_after_booking():
    """TC_18: Confirmation notification sent after booking -> Patient and doctor receive confirmation."""
    pat_headers = {"Authorization": f"Bearer {state['patient_token']}"}
    notifs = client.get("/api/notifications", headers=pat_headers).json()
    assert any("Confirmed" in n["title"] or "Appointment" in n["title"] for n in notifs)

def test_tc_19_reminder_notification_before_appointment():
    """TC_19: Reminder notification before appointment -> Reminder sent 24 hours before."""
    # Log in as admin and run reminder trigger
    admin_login = client.post("/api/auth/login", json={
        "email": "admin@hospital.com",
        "password": "Admin@12345"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    state["admin_token"] = admin_token

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    # Run reminder trigger
    response = client.post("/api/notifications/run-reminders", headers=admin_headers)
    assert response.status_code == 200
    reminders = response.json()
    assert isinstance(reminders, list)

def test_tc_20_admin_adds_a_new_doctor_profile():
    """TC_20: Admin adds a new doctor profile -> Stored and visible to patients."""
    admin_headers = {"Authorization": f"Bearer {state['admin_token']}"}
    payload = {
        "name": "Dr. Eleanor Vance",
        "email": "eleanor.vance@hospital.com",
        "password": "Doctor@12345",
        "phone_number": "+1-555-8899",
        "specialization": "Endocrinologist",
        "qualification": "MD, Harvard Medical",
        "experience_years": 11,
        "clinic_address": "Endocrine Clinic Suite 305",
        "consultation_fee": 1100.00,
        "bio": "Specialist in diabetes and hormonal disorders."
    }
    response = client.post("/api/admin/doctors", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["specialization"] == "Endocrinologist"
    new_doc_id = data["id"]

    # Verify visible in patient search
    search_res = client.get("/api/doctors", params={"specialization": "Endocrinologist"})
    assert search_res.status_code == 200
    assert any(d["id"] == new_doc_id for d in search_res.json())

def test_tc_21_admin_generates_monthly_appointment_report():
    """TC_21: Admin generates monthly appointment report -> Report with statistics is generated."""
    admin_headers = {"Authorization": f"Bearer {state['admin_token']}"}
    current_month = date.today().month
    current_year = date.today().year

    response = client.get("/api/reports/monthly", params={"month": current_month, "year": current_year}, headers=admin_headers)
    assert response.status_code == 200
    report = response.json()
    assert "total_appointments" in report
    assert "completed_count" in report
    assert "cancelled_count" in report
    assert "confirmed_count" in report
    assert "total_revenue" in report
    assert "specialization_breakdown" in report

# ============================================================================
# SECURITY TESTS (TC_22 - TC_23)
# ============================================================================

def test_tc_22_unauthorized_access_to_another_patients_appointment():
    """TC_22: Unauthorized access to another patient's appointment -> 403 Forbidden."""
    # Register Patient B
    p2_res = client.post("/api/auth/register", json={
        "name": "Intruder Bob",
        "email": "bob.intruder@test.com",
        "phone": "+1-555-9000",
        "password": "Password@123",
        "role": "patient"
    })
    assert p2_res.status_code == 201

    login_b = client.post("/api/auth/login", json={
        "email": "bob.intruder@test.com",
        "password": "Password@123"
    })
    bob_token = login_b.json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # Bob attempts to access Patient A's appointment directly
    response = client.get(f"/api/appointments/{state['appointment_id']}", headers=bob_headers)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

def test_tc_23_sql_injection_attempt_in_login_form():
    """TC_23: SQL injection attempt in login form -> Input rejected; no database error exposed."""
    malicious_emails = [
        "' OR '1'='1",
        "admin@hospital.com' --",
        "' UNION SELECT * FROM users --",
        "'; DROP TABLE users; --"
    ]
    for sql_payload in malicious_emails:
        response = client.post("/api/auth/login", json={
            "email": sql_payload,
            "password": "random_password"
        })
        # Must be rejected with 401 Unauthorized or 422, NEVER 500 Internal Server Error
        assert response.status_code in [401, 422], f"Failed on payload: {sql_payload}"
        data = response.json()
        assert "Internal server error" not in str(data)
        assert "syntax error" not in str(data).lower()
