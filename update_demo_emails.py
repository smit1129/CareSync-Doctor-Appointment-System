import os
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, init_db
from backend.app.models.user import User

def update_demo_emails():
    db = SessionLocal()
    
    # 1. Update Admin
    admin_user = db.query(User).filter(User.email == 'admin@hospital.com').first()
    if admin_user:
        admin_user.email = 'admin@demo.caresync.local'
    
    # 2. Update Doctor
    doc_user = db.query(User).filter(User.email == 'sarah.jenkins@hospital.com').first()
    if doc_user:
        doc_user.email = 'aarav.mehta@demo.caresync.local'
        doc_user.full_name = 'Dr. Aarav Mehta'
    
    # 3. Update Patient
    pat_user = db.query(User).filter(User.email == 'john.doe@gmail.com').first()
    if pat_user:
        pat_user.email = 'smit.gamit@demo.caresync.local'
        pat_user.full_name = 'Smit Gamit'
        
    db.commit()
    print("Successfully updated demo emails in the database.")
    db.close()

if __name__ == "__main__":
    init_db()
    update_demo_emails()
