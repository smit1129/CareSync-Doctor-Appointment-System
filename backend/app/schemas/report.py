from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DailyReportItem(BaseModel):
    appointment_id: str
    patient_name: str
    doctor_name: str
    specialization: str
    time: str
    status: str
    fee: float

class DailyReportResponse(BaseModel):
    date: str
    total_appointments: int
    confirmed_count: int
    completed_count: int
    cancelled_count: int
    total_revenue: float
    appointments: List[DailyReportItem]

class DoctorStat(BaseModel):
    doctor_id: str
    doctor_name: str
    specialization: str
    appointment_count: int

class MonthlyReportResponse(BaseModel):
    month: int
    year: int
    month_name: str
    total_appointments: int
    completed_count: int
    cancelled_count: int
    confirmed_count: int
    total_revenue: float
    specialization_breakdown: Dict[str, int]
    top_doctors: List[DoctorStat]
