import uuid
from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.database import get_db
from backend.app.models.user import User, Doctor
from backend.app.models.appointment import DoctorAvailability
from backend.app.schemas.doctor import (
    DoctorResponse,
    DoctorUpdate,
    DoctorAvailabilityCreate,
    DoctorAvailabilityResponse,
    TimeSlotResponse
)
from backend.app.core.security import get_current_user, require_roles
from backend.app.core.exceptions import NotFoundException, BadRequestException
from backend.app.services.appointment_service import AppointmentService, parse_time_str

router = APIRouter(prefix="/doctors", tags=["Doctors"])

def format_doctor_response(doctor: Doctor) -> dict:
    avail_list = []
    for a in doctor.availabilities:
        avail_list.append({
            "id": a.id,
            "doctor_id": a.doctor_id,
            "day_of_week": a.day_of_week,
            "start_time": a.start_time.strftime("%H:%M"),
            "end_time": a.end_time.strftime("%H:%M"),
            "slot_duration_minutes": a.slot_duration_minutes or 30,
            "is_active": a.is_active
        })

    return {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "name": doctor.user.full_name if doctor.user else "Unknown",
        "email": doctor.user.email if doctor.user else "",
        "phone_number": doctor.user.phone_number if doctor.user else None,
        "specialization": doctor.specialization,
        "qualification": doctor.qualification,
        "experience_years": doctor.experience_years,
        "clinic_address": doctor.clinic_address,
        "consultation_fee": doctor.consultation_fee,
        "bio": doctor.bio,
        "rating_avg": doctor.rating_avg,
        "rating_count": doctor.rating_count,
        "availabilities": avail_list
    }

@router.get("", response_model=List[DoctorResponse])
def get_doctors(
    specialization: Optional[str] = Query(None, description="Filter by specialization (TC_06, TC_07)"),
    search: Optional[str] = Query(None, description="Search by name or clinic"),
    db: Session = Depends(get_db)
):
    """
    Search and filter doctors.
    Enforces TC_06 (Cardiologist search) and TC_07 (No matching specialization).
    """
    query = db.query(Doctor).join(User, Doctor.user_id == User.id)

    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization.strip()}%"))

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_pattern),
                Doctor.specialization.ilike(search_pattern),
                Doctor.clinic_address.ilike(search_pattern)
            )
        )

    doctors = query.all()
    return [format_doctor_response(d) for d in doctors]

@router.get("/specializations", response_model=List[str])
def get_specializations(db: Session = Depends(get_db)):
    """Fetch distinct doctor specializations for UI filter buttons."""
    results = db.query(Doctor.specialization).distinct().all()
    specs = sorted(list(set(r[0] for r in results if r[0])))
    return specs

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor_by_id(doctor_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed doctor profile with availability schedules."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise NotFoundException("Doctor not found")
    return format_doctor_response(doctor)

@router.get("/{doctor_id}/slots", response_model=List[TimeSlotResponse])
def get_doctor_slots(
    doctor_id: str,
    target_date: date = Query(..., description="Date to fetch slots for (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Calculate and return free/booked time slots for a doctor on a specific date."""
    slots = AppointmentService.get_available_slots(db, doctor_id, target_date)
    return slots

@router.put("/me/profile", response_model=DoctorResponse)
def update_doctor_profile(
    req: DoctorUpdate,
    current_user: User = Depends(require_roles(["doctor"])),
    db: Session = Depends(get_db)
):
    """Doctor updates own profile information."""
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise NotFoundException("Doctor profile not found")

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

@router.post("/me/availability", response_model=List[DoctorAvailabilityResponse])
def set_doctor_availability(
    schedules: List[DoctorAvailabilityCreate],
    current_user: User = Depends(require_roles(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Doctor updates availability schedule (TC_13).
    Replaces existing schedules with new operational time slots.
    """
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise NotFoundException("Doctor profile not found")

    # Clear previous schedules and assign new ones
    db.query(DoctorAvailability).filter(DoctorAvailability.doctor_id == doctor.id).delete()

    created = []
    for s in schedules:
        avail = DoctorAvailability(
            id=str(uuid.uuid4()),
            doctor_id=doctor.id,
            day_of_week=s.day_of_week,
            start_time=parse_time_str(s.start_time),
            end_time=parse_time_str(s.end_time),
            slot_duration_minutes=s.slot_duration_minutes,
            is_active=s.is_active
        )
        db.add(avail)
        created.append(avail)

    db.commit()
    for c in created:
        db.refresh(c)

    return [
        {
            "id": c.id,
            "doctor_id": c.doctor_id,
            "day_of_week": c.day_of_week,
            "start_time": c.start_time.strftime("%H:%M"),
            "end_time": c.end_time.strftime("%H:%M"),
            "slot_duration_minutes": c.slot_duration_minutes,
            "is_active": c.is_active
        }
        for c in created
    ]

@router.get("/me/availability", response_model=List[DoctorAvailabilityResponse])
def get_my_availability(
    current_user: User = Depends(require_roles(["doctor"])),
    db: Session = Depends(get_db)
):
    """Fetch current logged-in doctor's availability schedules."""
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise NotFoundException("Doctor profile not found")

    return [
        {
            "id": a.id,
            "doctor_id": a.doctor_id,
            "day_of_week": a.day_of_week,
            "start_time": a.start_time.strftime("%H:%M"),
            "end_time": a.end_time.strftime("%H:%M"),
            "slot_duration_minutes": a.slot_duration_minutes or 30,
            "is_active": a.is_active
        }
        for a in doctor.availabilities
    ]
