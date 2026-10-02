from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Full Name of the patient")
    email: EmailStr = Field(..., description="Valid unique email address")
    phone: Optional[str] = Field(None, description="Contact phone number")
    password: str = Field(..., min_length=6, description="Account password")

class UserLoginRequest(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., description="Password")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    name: str
    email: str

class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email for password reset")

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="Reset verification token")
    new_password: str = Field(..., min_length=6, description="New secure password")

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    phone_number: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
