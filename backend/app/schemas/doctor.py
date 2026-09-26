from typing import Optional, List
from datetime import datetime, time
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class DoctorAvailabilityCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: str = Field(..., description="HH:MM:SS or HH:MM format")
    end_time: str = Field(..., description="HH:MM:SS or HH:MM format")
    slot_duration_minutes: int = Field(default=30, ge=10, le=120)
    is_active: bool = Field(default=True)

class DoctorAvailabilityResponse(BaseModel):
    id: str
    doctor_id: str
    day_of_week: int
    start_time: str
    end_time: str
    slot_duration_minutes: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class DoctorCreateByAdmin(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone_number: Optional[str] = None
    specialization: str = Field(..., min_length=2)
    qualification: str = Field(..., min_length=2)
    experience_years: int = Field(default=0, ge=0)
    clinic_address: str = Field(...)
    consultation_fee: float = Field(default=500.0, ge=0)
    bio: Optional[str] = None

class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    clinic_address: Optional[str] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None

class DoctorResponse(BaseModel):
    id: str
    user_id: str
    name: str
    email: str
    phone_number: Optional[str] = None
    specialization: str
    qualification: str
    experience_years: int
    clinic_address: str
    consultation_fee: float
    bio: Optional[str] = None
    rating_avg: float
    rating_count: int
    availabilities: List[DoctorAvailabilityResponse] = []

    model_config = ConfigDict(from_attributes=True)

class TimeSlotResponse(BaseModel):
    start_time: str
    end_time: str
    is_available: bool
