import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.models.payment import Payment
from backend.app.models.appointment import Appointment
from backend.app.models.notification import Notification
from backend.app.core.exceptions import BadRequestException, NotFoundException

class PaymentService:

    @staticmethod
    def process_payment(
        db: Session,
        appointment_id: str,
        patient_id: str,
        amount: float,
        payment_mode: str,
        simulate_failure: bool = False,
        card_number: Optional[str] = None,
        upi_id: Optional[str] = None
    ) -> Payment:
        """
        Processes appointment payment.
        Implements TC_15 (Success), TC_16 (Failure handling).
        """
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise NotFoundException("Appointment not found")

        # TC_16: Payment failure handling
        if simulate_failure or (card_number and card_number.startswith("0000")):
            # Record failed attempt or reject
            failed_txn_id = f"TXN-FAIL-{uuid.uuid4().hex[:8].upper()}"
            failed_payment = Payment(
                id=str(uuid.uuid4()),
                appointment_id=appointment_id,
                patient_id=patient_id,
                amount=amount,
                payment_mode=payment_mode,
                transaction_id=failed_txn_id,
                status="failed",
                receipt_number=f"REC-FAIL-{uuid.uuid4().hex[:6].upper()}"
            )
            db.add(failed_payment)
            db.commit()
            raise BadRequestException("Payment rejected: Invalid or expired card details")

        # TC_15: Successful payment processing
        txn_prefix = "UPI" if payment_mode.lower() == "upi" else "CARD"
        transaction_id = f"TXN-{txn_prefix}-{uuid.uuid4().hex[:10].upper()}"
        receipt_number = f"REC-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        payment = Payment(
            id=str(uuid.uuid4()),
            appointment_id=appointment_id,
            patient_id=patient_id,
            amount=amount,
            currency="INR",
            payment_mode=payment_mode,
            transaction_id=transaction_id,
            status="completed",
            receipt_number=receipt_number
        )
        db.add(payment)

        # Notify patient of successful transaction & receipt
        db.add(Notification(
            id=str(uuid.uuid4()),
            user_id=appointment.patient.user_id,
            title="Payment Successful",
            message=f"Payment of ₹{amount:.2f} received for appointment with Dr. {appointment.doctor.user.full_name}. Receipt: {receipt_number}",
            type="confirmation"
        ))

        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def refund_payment(
        db: Session,
        appointment_id: str,
        reason: Optional[str] = "Appointment cancellation"
    ) -> Payment:
        """
        Refunds a completed payment for a cancelled appointment (TC_17).
        """
        payment = db.query(Payment).filter(Payment.appointment_id == appointment_id).first()
        if not payment:
            raise NotFoundException("Payment record not found for this appointment")

        if payment.status != "completed":
            raise BadRequestException(f"Cannot refund payment in '{payment.status}' status")

        payment.status = "refunded"
        payment.refund_amount = payment.amount
        payment.refund_status = "refunded"

        db.add(Notification(
            id=str(uuid.uuid4()),
            user_id=payment.patient.user_id,
            title="Refund Processed",
            message=f"Your refund of ₹{payment.refund_amount:.2f} for appointment #{appointment_id[:8]} has been successfully processed to original payment mode.",
            type="status_change"
        ))

        db.commit()
        db.refresh(payment)
        return payment
