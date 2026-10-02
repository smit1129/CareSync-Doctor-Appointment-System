import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Float, Time, Date, Text, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class DoctorAvailability(Base):
    __tablename__ = "doctor_availabilities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday ... 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_duration_minutes = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    doctor = relationship("Doctor", back_populates="availabilities")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    appointment_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(30), nullable=False, default="Confirmed")  # Requested, Confirmed, Rejected, Cancelled, Rescheduled, Completed
    reason = Column(Text, nullable=True)
    consultation_fee_snapshot = Column(Float, nullable=True)  # Frozen fee at booking time
    cancellation_reason = Column(Text, nullable=True)
    rescheduled_from_id = Column(String(36), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    payment = relationship("Payment", back_populates="appointment", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("FeedbackRating", back_populates="appointment", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_doctor_appointment_date", "doctor_id", "appointment_date"),
        Index("idx_unique_active_doctor_slot", "doctor_id", "appointment_date", "start_time", 
              unique=True, sqlite_where=Column("status").notin_(["Cancelled", "Rejected"]), 
              postgresql_where=Column("status").notin_(["Cancelled", "Rejected"])),
    )
