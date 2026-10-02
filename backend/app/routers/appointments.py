import uuid
from datetime import datetime, date, time
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.models.user import User, Patient, Doctor
from backend.app.models.appointment import Appointment
from backend.app.models.notification import Notification
from backend.app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentCancel,
    AppointmentReschedule,
    DoctorAppointmentAction
)
from backend.app.core.security import get_current_user, require_roles
from backend.app.core.exceptions import (
    NotFoundException,
    ForbiddenException,
    BadRequestException,
    ConflictException
)
from backend.app.services.appointment_service import AppointmentService, parse_time_str

router = APIRouter(prefix="/appointments", tags=["Appointments"])

def format_appointment_response(apt: Appointment) -> dict:
    doc_name = apt.doctor.user.full_name if apt.doctor and apt.doctor.user else "Doctor"
    doc_spec = apt.doctor.specialization if apt.doctor else "General"
    pat_name = apt.patient.user.full_name if apt.patient and apt.patient.user else "Patient"

    return {
        "id": apt.id,
        "patient_id": apt.patient_id,
        "doctor_id": apt.doctor_id,
        "doctor_name": doc_name,
        "doctor_specialization": doc_spec,
        "patient_name": pat_name,
        "appointment_date": apt.appointment_date,
        "start_time": apt.start_time.strftime("%H:%M"),
        "end_time": apt.end_time.strftime("%H:%M"),
        "status": apt.status,
        "reason": apt.reason,
        "cancellation_reason": apt.cancellation_reason,
        "rescheduled_from_id": apt.rescheduled_from_id,
        "created_at": apt.created_at,
        "updated_at": apt.updated_at
    }

@router.post("/book", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    req: AppointmentCreate,
    current_user: User = Depends(require_roles(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Book an appointment (TC_08, TC_09, TC_10).
    - TC_08: Book available slot -> Confirmed
    - TC_09: Double-booking prevention -> 409 Conflict "Slot not available"
    - TC_10: Past date check -> 400 Validation error "Invalid date"
    """
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise BadRequestException("Patient profile not found for user")

    appointment = AppointmentService.book_appointment(
        db=db,
        patient_id=patient.id,
        doctor_id=req.doctor_id,
        appointment_date=req.appointment_date,
        start_time_str=req.start_time,
        reason=req.reason,
        initial_status="Requested"
    )
    return format_appointment_response(appointment)

@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: str,
    req: Optional[AppointmentCancel] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a confirmed appointment (TC_11).
    Frees the slot and triggers refund if paid (TC_17).
    """
    reason = req.cancellation_reason if req else "Cancelled by user"
    appointment = AppointmentService.cancel_appointment(
        db=db,
        appointment_id=appointment_id,
        user=current_user,
        cancellation_reason=reason
    )
    return format_appointment_response(appointment)

@router.post("/{appointment_id}/reschedule", response_model=AppointmentResponse)
def reschedule_appointment(
    appointment_id: str,
    req: AppointmentReschedule,
    current_user: User = Depends(require_roles(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Reschedule an existing appointment to a new date and time slot.
    Cancels old appointment and creates a new linked appointment.
    """
    old_apt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not old_apt:
        raise NotFoundException("Appointment not found")

    if current_user.role == "patient" and old_apt.patient.user_id != current_user.id:
        raise ForbiddenException("Access denied: You can only reschedule your own appointments")

    if old_apt.status not in ["Confirmed", "Payment Pending"]:
        raise BadRequestException(f"Appointment cannot be rescheduled from state: {old_apt.status}")

    # Cancel old appointment
    old_apt.status = "Rescheduled"
    old_apt.cancellation_reason = f"Rescheduled to {req.new_date} {req.new_start_time}"

    # Book new appointment
    new_apt = AppointmentService.book_appointment(
        db=db,
        patient_id=old_apt.patient_id,
        doctor_id=old_apt.doctor_id,
        appointment_date=req.new_date,
        start_time_str=req.new_start_time,
        reason=old_apt.reason,
        initial_status="Requested"
    )
    new_apt.rescheduled_from_id = old_apt.id
    db.commit()
    db.refresh(new_apt)

    return format_appointment_response(new_apt)

@router.get("/patient/history", response_model=List[AppointmentResponse])
def get_patient_appointment_history(
    current_user: User = Depends(require_roles(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    """
    View patient's appointment history (TC_12).
    Returns list of past and upcoming appointments.
    """
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        return []

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient.id
    ).order_by(desc(Appointment.appointment_date), desc(Appointment.start_time)).all()

    return [format_appointment_response(a) for a in appointments]

@router.get("/doctor/list", response_model=List[AppointmentResponse])
def get_doctor_appointments(
    current_user: User = Depends(require_roles(["doctor", "admin"])),
    date_filter: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Fetch appointments assigned to the logged-in doctor."""
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        return []

    query = db.query(Appointment).filter(Appointment.doctor_id == doctor.id)
    if date_filter:
        query = query.filter(Appointment.appointment_date == date_filter)

    appointments = query.order_by(Appointment.appointment_date, Appointment.start_time).all()
    return [format_appointment_response(a) for a in appointments]

@router.post("/{appointment_id}/doctor-action", response_model=AppointmentResponse)
def doctor_appointment_action(
    appointment_id: str,
    req: DoctorAppointmentAction,
    current_user: User = Depends(require_roles(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Doctor accepts or rejects a pending/requested appointment (TC_14).
    Action = Accept -> status = Confirmed.
    Action = Reject -> status = Rejected.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise NotFoundException("Appointment not found")

    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if current_user.role == "doctor" and appointment.doctor_id != doctor.id:
        raise ForbiddenException("Access denied: Not assigned to this appointment")

    action = req.action.strip().lower()
    if action == "accept":
        appointment.status = "Payment Pending"
        db.add(Notification(
            id=str(uuid.uuid4()),
            user_id=appointment.patient.user_id,
            title="Appointment Request Accepted",
            message=f"Your appointment request with Dr. {appointment.doctor.user.full_name} has been accepted. Please complete payment to confirm your appointment.",
            type="status_change"
        ))
    elif action == "reject":
        appointment.status = "Rejected"
        db.add(Notification(
            id=str(uuid.uuid4()),
            user_id=appointment.patient.user_id,
            title="Appointment Request Rejected",
            message=f"Dr. {appointment.doctor.user.full_name} is unavailable for appointment on {appointment.appointment_date}.",
            type="status_change"
        ))
    else:
        raise BadRequestException("Invalid action. Must be 'Accept' or 'Reject'")

    db.commit()
    db.refresh(appointment)
    return format_appointment_response(appointment)

@router.post("/{appointment_id}/complete", response_model=AppointmentResponse)
def mark_appointment_completed(
    appointment_id: str,
    current_user: User = Depends(require_roles(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    """Mark appointment as Completed after medical consultation."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise NotFoundException("Appointment not found")

    if current_user.role == "doctor" and appointment.doctor_id != current_user.doctor.id:
        raise ForbiddenException("Access denied: Not assigned to this appointment")

    appointment.status = "Completed"
    # Prompt patient for feedback
    db.add(Notification(
        id=str(uuid.uuid4()),
        user_id=appointment.patient.user_id,
        title="Consultation Completed - Feedback Requested",
        message=f"Your consultation with Dr. {appointment.doctor.user.full_name} is complete. Please rate your experience!",
        type="status_change"
    ))
    db.commit()
    db.refresh(appointment)
    return format_appointment_response(appointment)

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment_details(
    appointment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get appointment by ID.
    Enforces TC_22: Unauthorized access to another patient's appointment returns 403 Forbidden.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise NotFoundException("Appointment not found")

    # TC_22 Security check: A patient cannot access another patient's appointment
    if current_user.role == "patient":
        if not appointment.patient or appointment.patient.user_id != current_user.id:
            raise ForbiddenException("Access denied: You do not have permission to access this appointment")

    if current_user.role == "doctor":
        if not appointment.doctor or appointment.doctor.user_id != current_user.id:
            raise ForbiddenException("Access denied: You are not assigned to this appointment")

    return format_appointment_response(appointment)
