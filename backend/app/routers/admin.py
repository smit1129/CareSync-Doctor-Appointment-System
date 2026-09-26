import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User, Doctor, Patient
from backend.app.models.appointment import Appointment, DoctorAvailability
from backend.app.models.payment import Payment
from backend.app.schemas.doctor import DoctorCreateByAdmin, DoctorResponse, DoctorUpdate
from backend.app.schemas.patient import PatientResponse
from backend.app.core.security import require_roles, hash_password
from backend.app.core.exceptions import NotFoundException, BadRequestException
from backend.app.routers.doctors import format_doctor_response
from backend.app.routers.patients import format_patient_response

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

@router.post("/doctors", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def add_doctor_by_admin(
    req: DoctorCreateByAdmin,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Admin adds a new doctor profile (Req 2.1, TC_20).
    Doctor is immediately visible in patient search.
    """
    normalized_email = req.email.lower().strip()
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise BadRequestException("User email already exists")

    # Create User account
    user = User(
        id=str(uuid.uuid4()),
        email=normalized_email,
        password_hash=hash_password(req.password),
        full_name=req.name.strip(),
        role="doctor",
        phone_number=req.phone_number,
        is_active=True
    )
    db.add(user)
    db.flush()

    # Create Doctor profile
    doctor = Doctor(
        id=str(uuid.uuid4()),
        user_id=user.id,
        specialization=req.specialization.strip(),
        qualification=req.qualification.strip(),
        experience_years=req.experience_years,
        clinic_address=req.clinic_address.strip(),
        consultation_fee=req.consultation_fee,
        bio=req.bio or f"Specialist in {req.specialization}"
    )
    db.add(doctor)

    # Automatically add default weekday availability
    from datetime import time
    for day in range(5):  # Mon-Fri
        avail = DoctorAvailability(
            id=str(uuid.uuid4()),
            doctor_id=doctor.id,
            day_of_week=day,
            start_time=time(9, 0),
            end_time=time(17, 0),
            slot_duration_minutes=30,
            is_active=True
        )
        db.add(avail)

    db.commit()
    db.refresh(doctor)
    return format_doctor_response(doctor)

@router.put("/doctors/{doctor_id}", response_model=DoctorResponse)
def update_doctor_by_admin(
    doctor_id: str,
    req: DoctorUpdate,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Update doctor profile by Admin (Req 2.2)."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise NotFoundException("Doctor not found")

    if req.specialization is not None:
        doctor.specialization = req.specialization
    if req.qualification is not None:
        doctor.qualification = req.qualification
    if req.experience_years is not None:
        doctor.experience_years = req.experience_years
    if req.clinic_address is not None:
        doctor.clinic_address = req.clinic_address
    if req.consultation_fee is not None:
        doctor.consultation_fee = req.consultation_fee
    if req.bio is not None:
        doctor.bio = req.bio

    db.commit()
    db.refresh(doctor)
    return format_doctor_response(doctor)

@router.delete("/doctors/{doctor_id}")
def delete_doctor_by_admin(
    doctor_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Delete doctor account by Admin (Req 2.3)."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise NotFoundException("Doctor not found")

    user = doctor.user
    db.delete(doctor)
    if user:
        db.delete(user)
    db.commit()
    return {"message": f"Doctor profile {doctor_id} successfully deleted"}

@router.get("/patients", response_model=List[PatientResponse])
def get_all_patients_by_admin(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """List all registered patients for Admin management."""
    patients = db.query(Patient).all()
    return [format_patient_response(p) for p in patients]

@router.get("/stats")
def get_admin_dashboard_stats(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Hospital overview KPI cards for Admin dashboard."""
    total_doctors = db.query(Doctor).count()
    total_patients = db.query(Patient).count()
    total_appointments = db.query(Appointment).count()
    confirmed_appointments = db.query(Appointment).filter(Appointment.status == "Confirmed").count()
    completed_appointments = db.query(Appointment).filter(Appointment.status == "Completed").count()
    cancelled_appointments = db.query(Appointment).filter(Appointment.status.in_(["Cancelled", "Rejected"])).count()

    payments = db.query(Payment).filter(Payment.status == "completed").all()
    total_revenue = sum(p.amount for p in payments)

    return {
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "confirmed_appointments": confirmed_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "total_revenue": round(total_revenue, 2)
    }
