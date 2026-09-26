import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    appointment_id = Column(String(36), ForeignKey("appointments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    payment_mode = Column(String(30), nullable=False)  # card, upi, netbanking, cash
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(30), nullable=False, default="completed")  # pending, completed, failed, refunded
    receipt_number = Column(String(100), unique=True, nullable=False, index=True)
    refund_amount = Column(Float, default=0.0)
    refund_status = Column(String(30), nullable=True)  # none, initiated, refunded
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    appointment = relationship("Appointment", back_populates="payment")
    patient = relationship("Patient", back_populates="payments")
