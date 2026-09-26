from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User, Patient
from backend.app.schemas.patient import PatientResponse, PatientUpdate
from backend.app.core.security import get_current_user, require_roles
from backend.app.core.exceptions import NotFoundException, ForbiddenException

router = APIRouter(prefix="/patients", tags=["Patients"])

def format_patient_response(patient: Patient) -> dict:
    return {
        "id": patient.id,
        "user_id": patient.user_id,
        "name": patient.user.full_name if patient.user else "Unknown",
        "email": patient.user.email if patient.user else "",
        "phone_number": patient.user.phone_number if patient.user else None,
        "contact_no": patient.contact_no,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "blood_group": patient.blood_group,
        "medical_history": patient.medical_history,
        "created_at": patient.created_at
    }

@router.get("/me", response_model=PatientResponse)
def get_my_patient_profile(
    current_user: User = Depends(require_roles(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    """View current logged-in patient's profile (Req 4.1)."""
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise NotFoundException("Patient profile not found")
    return format_patient_response(patient)

@router.put("/me", response_model=PatientResponse)
def update_my_patient_profile(
    req: PatientUpdate,
    current_user: User = Depends(require_roles(["patient"])),
    db: Session = Depends(get_db)
):
    """Update current logged-in patient's profile (Req 4.2)."""
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise NotFoundException("Patient profile not found")

    if req.name is not None:
        patient.user.full_name = req.name.strip()
    if req.contact_no is not None:
        patient.contact_no = req.contact_no.strip()
        patient.user.phone_number = req.contact_no.strip()
    if req.date_of_birth is not None:
        patient.date_of_birth = req.date_of_birth
    if req.gender is not None:
        patient.gender = req.gender
    if req.blood_group is not None:
        patient.blood_group = req.blood_group
    if req.medical_history is not None:
        patient.medical_history = req.medical_history

    db.commit()
    db.refresh(patient)
    return format_patient_response(patient)

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient_by_id(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    View patient profile by ID (Req 4.1, User Story 2e).
    Permitted for Doctors (to view history prior to consultation) and Admins.
    A patient can only view their own profile.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise NotFoundException("Patient not found")

    if current_user.role == "patient" and patient.user_id != current_user.id:
        raise ForbiddenException("Access denied: You cannot view another patient's medical records")

    return format_patient_response(patient)
