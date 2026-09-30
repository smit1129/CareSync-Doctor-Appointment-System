import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def main():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        sys.exit(1)
        
    engine = create_engine(db_url)
    try:
        with engine.begin() as conn:
            # Update Users
            conn.execute(text("UPDATE users SET email='admin@demo.caresync.local', phone_number='+91 90000 00001' WHERE id='usr-admin-01'"))
            conn.execute(text("UPDATE users SET email='aarav.mehta@demo.caresync.local', full_name='Dr. Aarav Mehta', phone_number='+91 90000 10001' WHERE id='usr-doc-01'"))
            conn.execute(text("UPDATE users SET email='ananya.patel@demo.caresync.local', full_name='Dr. Ananya Patel', phone_number='+91 90000 10002' WHERE id='usr-doc-02'"))
            conn.execute(text("UPDATE users SET email='rohan.shah@demo.caresync.local', full_name='Dr. Rohan Shah', phone_number='+91 90000 10003' WHERE id='usr-doc-03'"))
            conn.execute(text("UPDATE users SET email='neha.desai@demo.caresync.local', full_name='Dr. Neha Desai', phone_number='+91 90000 10004' WHERE id='usr-doc-04'"))
            conn.execute(text("UPDATE users SET email='smit.gamit@demo.caresync.local', full_name='Smit Gamit', phone_number='+91 90000 20001' WHERE id='usr-pat-01'"))
            conn.execute(text("UPDATE users SET email='rahul.patel@demo.caresync.local', full_name='Rahul Patel', phone_number='+91 90000 20002' WHERE id='usr-pat-02'"))

            # Update Doctors (specialization didn't change for the IDs, just qualification and address)
            conn.execute(text("UPDATE doctors SET qualification='MBBS, MD, DM', clinic_address='Heart & Vascular Institute, SG Highway, Ahmedabad' WHERE id='doc-01'"))
            conn.execute(text("UPDATE doctors SET qualification='MBBS, MD', clinic_address='SkinCare Clinic, Vile Parle, Mumbai' WHERE id='doc-02'"))
            conn.execute(text("UPDATE doctors SET qualification='MBBS, MD, DNB', clinic_address='Children''s Health Center, Kothrud, Pune' WHERE id='doc-03'"))
            conn.execute(text("UPDATE doctors SET qualification='MBBS, MD, DM', clinic_address='Neuro Spine Hospital, Whitefield, Bengaluru' WHERE id='doc-04'"))

            # Update Patients
            conn.execute(text("UPDATE patients SET contact_no='+91 90000 20001' WHERE id='pat-01'"))
            conn.execute(text("UPDATE patients SET contact_no='+91 90000 20002' WHERE id='pat-02'"))
            
            print("Database demo data updated successfully.")
    except Exception as e:
        print(f"Error updating DB demo data: {e}")

if __name__ == "__main__":
    main()
