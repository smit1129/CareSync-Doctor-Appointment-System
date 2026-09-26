import uuid
from datetime import date, timedelta, datetime
from typing import List
from sqlalchemy.orm import Session

from backend.app.models.appointment import Appointment
from backend.app.models.notification import Notification

class ReminderService:

    @staticmethod
    def send_upcoming_reminders(db: Session, target_date: date = None) -> List[Notification]:
        """
        Sends reminder notifications for appointments occurring tomorrow / in 24 hours (TC_19).
        """
        if not target_date:
            target_date = date.today() + timedelta(days=1)

        upcoming_appointments = db.query(Appointment).filter(
            Appointment.appointment_date == target_date,
            Appointment.status == "Confirmed"
        ).all()

        created_notifications = []
        for apt in upcoming_appointments:
            patient_user = apt.patient.user
            doctor_name = apt.doctor.user.full_name
            time_str = apt.start_time.strftime("%I:%M %p")

            # Check if reminder already sent
            existing_reminder = db.query(Notification).filter(
                Notification.user_id == patient_user.id,
                Notification.type == "reminder",
                Notification.message.like(f"%{target_date}%")
            ).first()

            if not existing_reminder:
                notif = Notification(
                    id=str(uuid.uuid4()),
                    user_id=patient_user.id,
                    title="Upcoming Appointment Reminder",
                    message=f"Reminder: You have a scheduled appointment with Dr. {doctor_name} tomorrow ({target_date}) at {time_str}.",
                    type="reminder"
                )
                db.add(notif)
                created_notifications.append(notif)

        if created_notifications:
            db.commit()

        return created_notifications
