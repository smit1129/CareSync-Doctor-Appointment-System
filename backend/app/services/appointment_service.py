import uuid
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from fastapi import status

from backend.app.models.appointment import Appointment, DoctorAvailability
from backend.app.models.user import Doctor, Patient, User
from backend.app.models.notification import Notification
from backend.app.core.exceptions import ConflictException, NotFoundException, BadRequestException

def format_time_str(t: time) -> str:
    return t.strftime("%H:%M")

def parse_time_str(time_str: str) -> time:
    """Safely parse HH:MM or HH:MM:SS string to time object."""
    parts = time_str.strip().split(":")
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0
    seconds = int(parts[2]) if len(parts) > 2 else 0
    return time(hours, minutes, seconds)

class AppointmentService:

    @staticmethod
    def get_available_slots(db: Session, doctor_id: str, target_date: date) -> List[Dict[str, Any]]:
        """Calculate all slots for a doctor on target_date and mark if available."""
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise NotFoundException("Doctor not found")

        day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
        availabilities = db.query(DoctorAvailability).filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.day_of_week == day_of_week,
            DoctorAvailability.is_active == True
        ).all()

        # If no explicit availability on this day, doctor is not available
        if not availabilities:
            return []

        # Get existing active bookings for this doctor on target_date
        booked_appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == target_date,
            Appointment.status.notin_(["Cancelled", "Rejected"])
        ).all()

        booked_start_times = {apt.start_time.strftime("%H:%M") for apt in booked_appointments}

        slots = []
        for avail in availabilities:
            slot_duration = timedelta(minutes=avail.slot_duration_minutes or 30)
            current_dt = datetime.combine(target_date, avail.start_time)
            end_dt = datetime.combine(target_date, avail.end_time)

            while current_dt + slot_duration <= end_dt:
                slot_start_time = current_dt.time()
                slot_end_time = (current_dt + slot_duration).time()
                start_str = slot_start_time.strftime("%H:%M")
                end_str = slot_end_time.strftime("%H:%M")

                is_booked = start_str in booked_start_times
                slots.append({
                    "start_time": start_str,
                    "end_time": end_str,
                    "is_available": not is_booked
                })
                current_dt += slot_duration

        return slots

    @staticmethod
    def book_appointment(
        db: Session,
        patient_id: str,
        doctor_id: str,
        appointment_date: date,
        start_time_str: str,
        reason: Optional[str] = None,
        initial_status: str = "Confirmed"
    ) -> Appointment:
        """
        Concurrency-safe appointment booking with conflict checking and database transaction.
        Enforces TC_08, TC_09, TC_10.
        """
        # TC_10: Validate date is not in the past
        if appointment_date < date.today():
            raise BadRequestException("Invalid date: Appointment date cannot be in the past")

        # Validate doctor exists
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise NotFoundException("Doctor not found")

        # Validate patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise NotFoundException("Patient not found")

        # Validate doctor availability (Requirement 3)
        available_slots = AppointmentService.get_available_slots(db, doctor_id, appointment_date)
        requested_slot = next((slot for slot in available_slots if slot["start_time"] == start_time_str), None)
        
        if not requested_slot:
            raise BadRequestException(f"Invalid slot: Doctor is not available at {start_time_str} on {appointment_date}")
            
        if not requested_slot["is_available"]:
            raise ConflictException("Slot not available: Another appointment is already booked for this time")

        parsed_start = parse_time_str(start_time_str)
        parsed_end = parse_time_str(requested_slot["end_time"])

        # Concurrency & Double-Booking Protection (TC_09):
        # We query for any active appointment matching doctor_id, date, and start_time
        # In a transactional lock
        existing_appointment = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.start_time == parsed_start,
            Appointment.status.notin_(["Cancelled", "Rejected"])
        ).with_for_update(nowait=False).first() if db.bind.name == "postgresql" else db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.start_time == parsed_start,
            Appointment.status.notin_(["Cancelled", "Rejected"])
        ).first()

        if existing_appointment:
            raise ConflictException("Slot not available: Another appointment is already booked for this time")

        # Create appointment record
        appointment = Appointment(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            start_time=parsed_start,
            end_time=parsed_end,
            status=initial_status,
            reason=reason or "General Consultation"
        )
        db.add(appointment)

        # Create confirmation notifications for both Patient and Doctor (TC_18)
        doctor_user = doctor.user
        patient_user = patient.user

        db.add(Notification(
            id=str(uuid.uuid4()),
            user_id=patient_user.id,
            title="Appointment Confirmed",
            message=f"Your appointment with Dr. {doctor_user.full_name} ({doctor.specialization}) on {appointment_date} at {start_time_str} is confirmed.",
            type="confirmation"
        ))

        db.add(Notification(
            id=str(uuid.uuid4()),
            user_id=doctor_user.id,
            title="New Appointment Booked",
            message=f"Patient {patient_user.full_name} has booked an appointment for {appointment_date} at {start_time_str}.",
            type="confirmation"
        ))

        try:
            db.commit()
            db.refresh(appointment)
            return appointment
        except IntegrityError:
            db.rollback()
            raise ConflictException("Slot not available: Another appointment is already booked for this time")

    @staticmethod
    def cancel_appointment(
        db: Session,
        appointment_id: str,
        user: User,
        cancellation_reason: Optional[str] = "Cancelled by user"
    ) -> Appointment:
        """
        Cancel an appointment, freeing the slot (TC_11).
        Triggers refund if already paid (TC_17).
        """
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise NotFoundException("Appointment not found")

        # Enforce authorization: Patient can only cancel their own; Doctor can cancel theirs; Admin can cancel any
        if user.role == "patient":
            if not appointment.patient or appointment.patient.user_id != user.id:
                raise BadRequestException("Access denied: You can only cancel your own appointments")
        elif user.role == "doctor":
            if not appointment.doctor or appointment.doctor.user_id != user.id:
                raise BadRequestException("Access denied: You can only cancel your own appointments")

        if appointment.status == "Cancelled":
            return appointment

        appointment.status = "Cancelled"
        appointment.cancellation_reason = cancellation_reason

        # Check for completed payment to initiate refund (TC_17)
        if appointment.payment and appointment.payment.status == "completed":
            appointment.payment.status = "refunded"
            appointment.payment.refund_amount = appointment.payment.amount
            appointment.payment.refund_status = "refunded"

        # Send notifications
        patient_user_id = appointment.patient.user_id
        doctor_user_id = appointment.doctor.user_id

        db.add(Notification(
            id=str(uuid.uuid4()),
            user_id=patient_user_id,
            title="Appointment Cancelled",
            message=f"Your appointment on {appointment.appointment_date} has been cancelled. If paid, your refund has been processed.",
            type="status_change"
        ))

        db.add(Notification(
            id=str(uuid.uuid4()),
            user_id=doctor_user_id,
            title="Appointment Cancelled",
            message=f"The appointment on {appointment.appointment_date} with patient {appointment.patient.user.full_name} has been cancelled.",
            type="status_change"
        ))

        db.commit()
        db.refresh(appointment)
        return appointment
