from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.notification import Notification
from backend.app.schemas.notification import NotificationResponse
from backend.app.core.security import get_current_user
from backend.app.core.exceptions import NotFoundException
from backend.app.services.reminder_service import ReminderService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationResponse])
def get_user_notifications(
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch notifications for the logged-in user (TC_18, TC_19)."""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    notifications = query.order_by(desc(Notification.created_at)).all()
    return notifications

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise NotFoundException("Notification not found")

    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif

@router.post("/run-reminders", response_model=List[NotificationResponse])
def trigger_upcoming_reminders(
    target_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger automatic 24-hour appointment reminders (TC_19).
    Sends notifications to patients with visits scheduled for tomorrow.
    """
    new_notifs = ReminderService.send_upcoming_reminders(db, target_date)
    return new_notifs
