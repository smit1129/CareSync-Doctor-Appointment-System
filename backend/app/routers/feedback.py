import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.models.user import User, Patient, Doctor
from backend.app.models.appointment import Appointment
from backend.app.models.feedback import FeedbackRating
from backend.app.schemas.feedback import FeedbackCreate, FeedbackResponse
from backend.app.core.security import get_current_user, require_roles
from backend.app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException

router = APIRouter(prefix="/feedback", tags=["Feedback & Ratings"])

def format_feedback(fb: FeedbackRating) -> dict:
    pat_name = fb.patient.user.full_name if fb.patient and fb.patient.user else "Anonymous"
    return {
        "id": fb.id,
        "appointment_id": fb.appointment_id,
        "patient_id": fb.patient_id,
        "patient_name": pat_name,
        "doctor_id": fb.doctor_id,
        "rating": fb.rating,
        "comment": fb.comment,
        "created_at": fb.created_at
    }

@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    req: FeedbackCreate,
    current_user: User = Depends(require_roles(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Submit rating (1-5) and feedback for a completed consultation.
    Recalculates doctor average rating and rating count.
    """
    appointment = db.query(Appointment).filter(Appointment.id == req.appointment_id).first()
    if not appointment:
        raise NotFoundException("Appointment not found")

    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if current_user.role == "patient" and appointment.patient_id != patient.id:
        raise ForbiddenException("Access denied: You can only review your own appointments")

    # Check if feedback already submitted
    existing_fb = db.query(FeedbackRating).filter(FeedbackRating.appointment_id == req.appointment_id).first()
    if existing_fb:
        raise BadRequestException("Feedback has already been submitted for this appointment")

    new_feedback = FeedbackRating(
        id=str(uuid.uuid4()),
        appointment_id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        rating=req.rating,
        comment=req.comment
    )
    db.add(new_feedback)

    # Recalculate doctor ratings
    doctor = appointment.doctor
    all_ratings = db.query(FeedbackRating.rating).filter(FeedbackRating.doctor_id == doctor.id).all()
    total_ratings = [r[0] for r in all_ratings] + [req.rating]
    doctor.rating_count = len(total_ratings)
    doctor.rating_avg = round(sum(total_ratings) / len(total_ratings), 2)

    db.commit()
    db.refresh(new_feedback)
    return format_feedback(new_feedback)

@router.get("/doctor/{doctor_id}", response_model=List[FeedbackResponse])
def get_doctor_feedbacks(doctor_id: str, db: Session = Depends(get_db)):
    """Fetch patient feedback and reviews for a doctor."""
    feedbacks = db.query(FeedbackRating).filter(
        FeedbackRating.doctor_id == doctor_id
    ).order_by(desc(FeedbackRating.created_at)).all()

    return [format_feedback(fb) for fb in feedbacks]
