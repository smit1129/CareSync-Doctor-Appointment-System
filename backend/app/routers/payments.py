from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User, Patient
from backend.app.models.payment import Payment
from backend.app.models.appointment import Appointment
from backend.app.schemas.payment import (
    PaymentProcessRequest,
    PaymentResponse,
    ReceiptResponse,
    RefundRequest
)
from backend.app.core.security import get_current_user, require_roles
from backend.app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from backend.app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/process", response_model=PaymentResponse)
def process_appointment_payment(
    req: PaymentProcessRequest,
    current_user: User = Depends(require_roles(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Process payment for appointment (TC_15, TC_16).
    - TC_15: Successful payment -> status 'completed', receipt number generated
    - TC_16: Payment failure -> rejected with 400 Bad Request
    """
    appointment = db.query(Appointment).filter(Appointment.id == req.appointment_id).first()
    if not appointment:
        raise NotFoundException("Appointment not found")

    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    patient_id = patient.id if patient else appointment.patient_id

    if current_user.role == "patient" and (not patient or appointment.patient_id != patient.id):
        raise ForbiddenException("Access denied: You can only pay for your own appointments")

    if appointment.status not in ["Payment Pending"]:
        raise BadRequestException(f"Appointment is not in a payable state: {appointment.status}")

    # Check if already paid
    if appointment.payment and appointment.payment.status == "completed":
        return appointment.payment

    # Server-authoritative amount calculation from the fee snapshot captured at booking time
    # Falls back to current fee for pre-existing appointments without a snapshot
    actual_amount = float(appointment.consultation_fee_snapshot or appointment.doctor.consultation_fee)

    payment = PaymentService.process_payment(
        db=db,
        appointment_id=req.appointment_id,
        patient_id=patient.id if patient else appointment.patient_id,
        amount=actual_amount,
        payment_mode=req.payment_mode,
        simulate_failure=bool(req.simulate_failure),
        card_number=req.card_number,
        upi_id=req.upi_id
    )

    return payment

@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: str,
    req: RefundRequest = None,
    current_user: User = Depends(require_roles(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    """Refund a completed payment (TC_17)."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise NotFoundException("Payment record not found")

    # Authorize: Patient of this payment, or admin
    if current_user.role == "patient" and payment.patient.user_id != current_user.id:
        raise ForbiddenException("Access denied: Not your payment record")

    refunded_payment = PaymentService.refund_payment(
        db=db,
        appointment_id=payment.appointment_id,
        reason=req.reason if req else "Cancelled"
    )
    return refunded_payment

@router.get("/receipt/{receipt_number}", response_model=ReceiptResponse)
def get_payment_receipt(
    receipt_number: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full official receipt details by receipt number."""
    payment = db.query(Payment).filter(Payment.receipt_number == receipt_number).first()
    if not payment:
        raise NotFoundException("Receipt not found")

    # Authorize: Patient of this payment, or admin
    if current_user.role == "patient" and payment.patient.user_id != current_user.id:
        raise ForbiddenException("Access denied: Not your payment receipt")
    if current_user.role not in ["patient", "admin"]:
        raise ForbiddenException("Access denied: Invalid role")

    appointment = payment.appointment
    doctor = appointment.doctor
    patient = payment.patient

    return ReceiptResponse(
        receipt_number=payment.receipt_number,
        transaction_id=payment.transaction_id,
        appointment_id=appointment.id,
        doctor_name=doctor.user.full_name if doctor and doctor.user else "Doctor",
        patient_name=patient.user.full_name if patient and patient.user else "Patient",
        appointment_date=str(appointment.appointment_date),
        appointment_time=appointment.start_time.strftime("%H:%M"),
        amount=payment.amount,
        currency=payment.currency,
        payment_mode=payment.payment_mode,
        status=payment.status,
        payment_date=payment.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )
