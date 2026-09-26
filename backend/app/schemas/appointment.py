from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

class AppointmentCreate(BaseModel):
    doctor_id: str = Field(..., description="Target Doctor ID")
    appointment_date: date = Field(..., description="Target date (must be today or future)")
    start_time: str = Field(..., description="Start time (HH:MM or HH:MM:SS)")
    end_time: Optional[str] = Field(None, description="End time (defaults to start_time + 30 min)")
    reason: Optional[str] = Field(None, description="Reason for consultation")
    initial_status: Optional[str] = Field("Confirmed", description="Confirmed or Requested")

    @field_validator("appointment_date")
    @classmethod
    def validate_future_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Invalid date: Appointment date cannot be in the past")
        return v

class AppointmentCancel(BaseModel):
    cancellation_reason: Optional[str] = Field("Cancelled by patient", description="Reason for cancellation")

class AppointmentReschedule(BaseModel):
    new_date: date = Field(..., description="New appointment date")
    new_start_time: str = Field(..., description="New start time")

    @field_validator("new_date")
    @classmethod
    def validate_reschedule_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Invalid date: Rescheduled date cannot be in the past")
        return v

class DoctorAppointmentAction(BaseModel):
    action: str = Field(..., description="Accept or Reject")

class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    doctor_name: Optional[str] = None
    doctor_specialization: Optional[str] = None
    patient_name: Optional[str] = None
    appointment_date: date
    start_time: str
    end_time: str
    status: str
    reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    rescheduled_from_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
