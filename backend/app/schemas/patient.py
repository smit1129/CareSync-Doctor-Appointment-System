from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    contact_no: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_history: Optional[str] = None

class PatientResponse(BaseModel):
    id: str
    user_id: str
    name: str
    email: str
    phone_number: Optional[str] = None
    contact_no: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_history: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
