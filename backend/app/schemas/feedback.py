from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class FeedbackCreate(BaseModel):
    appointment_id: str = Field(..., description="ID of completed appointment")
    rating: int = Field(..., ge=1, le=5, description="Star rating between 1 and 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Patient review feedback")

class FeedbackResponse(BaseModel):
    id: str
    appointment_id: str
    patient_id: str
    patient_name: Optional[str] = None
    doctor_id: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
