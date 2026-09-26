import calendar
from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from backend.app.database import get_db
from backend.app.models.user import User, Doctor
from backend.app.models.appointment import Appointment
from backend.app.models.payment import Payment
from backend.app.schemas.report import DailyReportResponse, MonthlyReportResponse, DailyReportItem, DoctorStat
from backend.app.core.security import require_roles

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/daily", response_model=DailyReportResponse)
def get_daily_report(
    report_date: Optional[date] = Query(None, description="Date for report, defaults to today"),
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Daily Appointment Report (Req 5.1).
    Input: Daily appointment records.
    Output: Daily appointment summary with breakdown.
    """
    target_date = report_date or date.today()

    appointments = db.query(Appointment).filter(
        Appointment.appointment_date == target_date
    ).all()

    items = []
    confirmed_count = 0
    completed_count = 0
    cancelled_count = 0
    total_revenue = 0.0

    for a in appointments:
        if a.status == "Confirmed":
            confirmed_count += 1
        elif a.status == "Completed":
            completed_count += 1
        elif a.status in ["Cancelled", "Rejected"]:
            cancelled_count += 1

        fee = a.doctor.consultation_fee if a.doctor else 0.0
        if a.payment and a.payment.status == "completed":
            total_revenue += a.payment.amount

        items.append(DailyReportItem(
            appointment_id=a.id,
            patient_name=a.patient.user.full_name if a.patient and a.patient.user else "Patient",
            doctor_name=a.doctor.user.full_name if a.doctor and a.doctor.user else "Doctor",
            specialization=a.doctor.specialization if a.doctor else "General",
            time=a.start_time.strftime("%H:%M"),
            status=a.status,
            fee=fee
        ))

    return DailyReportResponse(
        date=str(target_date),
        total_appointments=len(appointments),
        confirmed_count=confirmed_count,
        completed_count=completed_count,
        cancelled_count=cancelled_count,
        total_revenue=round(total_revenue, 2),
        appointments=items
    )

@router.get("/monthly", response_model=MonthlyReportResponse)
def get_monthly_report(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2035, description="Year"),
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Monthly Appointment Report (Req 5.2, TC_21).
    Admin generates monthly appointment report with statistical breakdown.
    """
    # Query appointments in month and year
    appointments = db.query(Appointment).filter(
        extract('month', Appointment.appointment_date) == month,
        extract('year', Appointment.appointment_date) == year
    ).all()

    total_count = len(appointments)
    confirmed_count = 0
    completed_count = 0
    cancelled_count = 0
    total_revenue = 0.0
    spec_counts = {}
    doc_counts = {}

    for a in appointments:
        if a.status == "Confirmed":
            confirmed_count += 1
        elif a.status == "Completed":
            completed_count += 1
        elif a.status in ["Cancelled", "Rejected"]:
            cancelled_count += 1

        if a.payment and a.payment.status == "completed":
            total_revenue += a.payment.amount

        if a.doctor:
            spec = a.doctor.specialization
            spec_counts[spec] = spec_counts.get(spec, 0) + 1

            d_id = a.doctor_id
            doc_counts[d_id] = doc_counts.get(d_id, 0) + 1

    # Top doctors
    top_docs = []
    for d_id, count in sorted(doc_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        doc = db.query(Doctor).filter(Doctor.id == d_id).first()
        if doc:
            top_docs.append(DoctorStat(
                doctor_id=doc.id,
                doctor_name=doc.user.full_name if doc.user else "Doctor",
                specialization=doc.specialization,
                appointment_count=count
            ))

    month_name = calendar.month_name[month]

    return MonthlyReportResponse(
        month=month,
        year=year,
        month_name=month_name,
        total_appointments=total_count,
        confirmed_count=confirmed_count,
        completed_count=completed_count,
        cancelled_count=cancelled_count,
        total_revenue=round(total_revenue, 2),
        specialization_breakdown=spec_counts,
        top_doctors=top_docs
    )
