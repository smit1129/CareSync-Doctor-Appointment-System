import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from backend.app.core.limiter import limiter

from backend.app.database import get_db
from backend.app.models.user import User, Patient, Doctor, PasswordReset
from backend.app.models.notification import Notification
from backend.app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserResponse
)
from backend.app.core.security import hash_password, verify_password, create_access_token, get_current_user
from backend.app.core.exceptions import BadRequestException, UnauthorizedException, NotFoundException

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, req: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Patient Registration (Req 1.1, TC_01, TC_02).
    Validates user details, checks email uniqueness, securely hashes password.
    """
    normalized_email = req.email.lower().strip()
    # TC_02: Check if email is already registered
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise BadRequestException("Email already registered")

    new_user = User(
        id=str(uuid.uuid4()),
        email=normalized_email,
        password_hash=hash_password(req.password),
        full_name=req.name.strip(),
        role="patient",
        phone_number=req.phone,
        is_active=True
    )
    db.add(new_user)
    db.flush()

    patient_profile = Patient(
        id=str(uuid.uuid4()),
        user_id=new_user.id,
        contact_no=req.phone
    )
    db.add(patient_profile)

    # Welcome notification
    db.add(Notification(
        id=str(uuid.uuid4()),
        user_id=new_user.id,
        title="Welcome to Doctor Appointment System",
        message="Your account has been created successfully. You can now book appointments seamlessly.",
        type="system"
    ))

    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, req: UserLoginRequest, db: Session = Depends(get_db)):
    """
    User Login (Req 1.2, TC_03, TC_04, TC_23).
    Parameterized ORM query protects against SQL injection.
    Validates credentials and issues JWT token.
    """
    normalized_email = req.email.lower().strip()
    user = db.query(User).filter(User.email == normalized_email).first()

    # TC_04 & TC_23: Invalid credentials or malicious string rejected safely
    if not user or not verify_password(req.password, user.password_hash):
        raise UnauthorizedException("Invalid credentials")

    if not user.is_active:
        raise UnauthorizedException("Account is inactive. Please contact administrator.")

    access_token = create_access_token(
        data={"sub": user.id, "role": user.role, "email": user.email, "name": user.full_name}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        role=user.role,
        name=user.full_name,
        email=user.email
    )

@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(request: Request, req: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Password reset request (TC_05).
    Sends password reset link/token to registered email.
    """
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user:
        return {"message": "If the account exists, a password reset link has been sent."}

    reset_token = uuid.uuid4().hex
    reset_entry = PasswordReset(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token=reset_token,
        expires_at=datetime.utcnow() + timedelta(hours=2)
    )
    db.add(reset_entry)
    db.commit()

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"DEMO MODE / LOCAL DEV: Password reset token for {req.email} is: {reset_token}")

    return {
        "message": "If the account exists, a password reset link has been sent."
    }

@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(request: Request, req: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Confirm password reset using token and update password.
    """
    reset_entry = db.query(PasswordReset).filter(
        PasswordReset.token == req.token,
        PasswordReset.used == False,
        PasswordReset.expires_at > datetime.utcnow()
    ).first()

    if not reset_entry:
        raise BadRequestException("Invalid or expired password reset token")

    user = reset_entry.user
    user.password_hash = hash_password(req.new_password)
    reset_entry.used = True
    db.commit()

    return {"message": "Password updated successfully. You can now login with your new password."}

@router.get("/me")
def get_current_user_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Fetch the currently authenticated user with associated profile information.
    """
    patient_id = user.patient.id if user.patient else None
    doctor_id = user.doctor.id if user.doctor else None

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "phone_number": user.phone_number,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "created_at": user.created_at
    }
