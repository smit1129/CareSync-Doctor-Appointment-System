from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class PaymentProcessRequest(BaseModel):
    appointment_id: str = Field(..., description="ID of the appointment to pay for")
    amount: float = Field(..., gt=0, description="Payment amount in INR")
    payment_mode: str = Field(..., description="card, upi, netbanking, or cash")
    # Safe demo card/UPI inputs:
    card_number: Optional[str] = Field(None, description="Last 4 digits or tokenized card")
    card_expiry: Optional[str] = Field(None, description="MM/YY format")
    upi_id: Optional[str] = Field(None, description="UPI Virtual Payment Address e.g. name@upi")
    simulate_failure: Optional[bool] = Field(False, description="Flag to simulate payment failure for TC_16")

class RefundRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Reason for refund")

class PaymentResponse(BaseModel):
    id: str
    appointment_id: str
    patient_id: str
    amount: float
    currency: str
    payment_mode: str
    transaction_id: str
    status: str
    receipt_number: str
    refund_amount: float
    refund_status: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReceiptResponse(BaseModel):
    receipt_number: str
    transaction_id: str
    appointment_id: str
    doctor_name: str
    patient_name: str
    appointment_date: str
    appointment_time: str
    amount: float
    currency: str
    payment_mode: str
    status: str
    payment_date: str
