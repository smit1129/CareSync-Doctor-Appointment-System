import uuid
from datetime import date, time, timedelta, datetime
from sqlalchemy.orm import Session

from backend.app.models.user import User, Doctor, Patient
from backend.app.models.appointment import Appointment, DoctorAvailability
from backend.app.models.payment import Payment
from backend.app.models.notification import Notification
from backend.app.models.feedback import FeedbackRating
from backend.app.core.security import hash_password
from backend.app.core.logging_config import logger

def seed_database(db: Session):
    """Populate default seed records if database has no users."""
    existing_users = db.query(User).first()
    if existing_users:
        logger.info("Database already seeded. Skipping initial data population.")
        return

    logger.info("Seeding initial healthcare dataset...")

    # Default password for all seed accounts
    admin_pw = hash_password("Admin@12345")
    doc_pw = hash_password("Doctor@12345")
    pat_pw = hash_password("Patient@12345")

    # 1. ADMIN USER
    admin_user = User(
        id="usr-admin-01",
        email="admin@hospital.com",
        password_hash=admin_pw,
        full_name="Hospital Administrator",
        role="admin",
        phone_number="+1-555-0100",
        is_active=True
    )
    db.add(admin_user)

    # 2. DOCTORS
    doctors_info = [
        {
            "user_id": "usr-doc-01",
            "doc_id": "doc-01",
            "name": "Dr. Sarah Jenkins",
            "email": "sarah.jenkins@hospital.com",
            "phone": "+1-555-0101",
            "specialization": "Cardiologist",
            "qualification": "MD, FACC, Harvard Medical",
            "exp": 14,
            "address": "Heart & Vascular Suite 402, Metro Health Center",
            "fee": 1200.0,
            "bio": "Board-certified cardiologist specializing in non-invasive cardiovascular treatments, preventative care, and heart failure management.",
            "rating": 4.9,
            "count": 28
        },
        {
            "user_id": "usr-doc-02",
            "doc_id": "doc-02",
            "name": "Dr. Marcus Vance",
            "email": "marcus.vance@hospital.com",
            "phone": "+1-555-0102",
            "specialization": "Dermatologist",
            "qualification": "MD, American Board of Dermatology",
            "exp": 10,
            "address": "Skin & Wellness Center, Level 2",
            "fee": 900.0,
            "bio": "Specialist in clinical and cosmetic dermatology, acne therapies, eczema, and skin cancer screenings.",
            "rating": 4.8,
            "count": 19
        },
        {
            "user_id": "usr-doc-03",
            "doc_id": "doc-03",
            "name": "Dr. Priya Sharma",
            "email": "priya.sharma@hospital.com",
            "phone": "+1-555-0103",
            "specialization": "Pediatrician",
            "qualification": "MBBS, MD Pediatrics, Johns Hopkins",
            "exp": 8,
            "address": "Childrens Care Wing, Room 108",
            "fee": 800.0,
            "bio": "Compassionate pediatric specialist dedicated to child health, vaccinations, growth monitoring, and developmental wellbeing.",
            "rating": 5.0,
            "count": 35
        },
        {
            "user_id": "usr-doc-04",
            "doc_id": "doc-04",
            "name": "Dr. Alex Mercer",
            "email": "alex.mercer@hospital.com",
            "phone": "+1-555-0104",
            "specialization": "Neurologist",
            "qualification": "MD, PhD Neuroscience, Oxford",
            "exp": 16,
            "address": "Brain & Nerve Institute, 6th Floor",
            "fee": 1500.0,
            "bio": "Leading neurologist treating migraines, neurological disorders, cognitive disorders, and stroke rehabilitation.",
            "rating": 4.9,
            "count": 22
        },
        {
            "user_id": "usr-doc-05",
            "doc_id": "doc-05",
            "name": "Dr. Emily Stone",
            "email": "emily.stone@hospital.com",
            "phone": "+1-555-0105",
            "specialization": "General Physician",
            "qualification": "MBBS, General Medicine",
            "exp": 7,
            "address": "Primary Care Wing, Clinic A",
            "fee": 600.0,
            "bio": "Experienced family physician focusing on routine check-ups, lifestyle diseases, diabetes and hypertension management.",
            "rating": 4.7,
            "count": 14
        }
    ]

    for d in doctors_info:
        u = User(
            id=d["user_id"],
            email=d["email"],
            password_hash=doc_pw,
            full_name=d["name"],
            role="doctor",
            phone_number=d["phone"],
            is_active=True
        )
        db.add(u)
        db.flush()

        doc = Doctor(
            id=d["doc_id"],
            user_id=u.id,
            specialization=d["specialization"],
            qualification=d["qualification"],
            experience_years=d["exp"],
            clinic_address=d["address"],
            consultation_fee=d["fee"],
            bio=d["bio"],
            rating_avg=d["rating"],
            rating_count=d["count"]
        )
        db.add(doc)

        # Add Monday to Saturday availability 09:00 - 17:00
        for day in range(6):
            avail = DoctorAvailability(
                id=str(uuid.uuid4()),
                doctor_id=doc.id,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                slot_duration_minutes=30,
                is_active=True
            )
            db.add(avail)

    # 3. PATIENTS
    patients_info = [
        {
            "user_id": "usr-pat-01",
            "pat_id": "pat-01",
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "phone": "+1-555-0150",
            "dob": date(1988, 4, 12),
            "gender": "Male",
            "blood": "O+",
            "history": "Mild hypertension, taking Losartan 25mg daily. No known drug allergies."
        },
        {
            "user_id": "usr-pat-02",
            "pat_id": "pat-02",
            "name": "Alice Smith",
            "email": "alice.smith@gmail.com",
            "phone": "+1-555-0151",
            "dob": date(1993, 9, 25),
            "gender": "Female",
            "blood": "A+",
            "history": "Asthma, seasonal pollen allergy. Uses albuterol inhaler as needed."
        }
    ]

    for p in patients_info:
        u = User(
            id=p["user_id"],
            email=p["email"],
            password_hash=pat_pw,
            full_name=p["name"],
            role="patient",
            phone_number=p["phone"],
            is_active=True
        )
        db.add(u)
        db.flush()

        pat = Patient(
            id=p["pat_id"],
            user_id=u.id,
            contact_no=p["phone"],
            date_of_birth=p["dob"],
            gender=p["gender"],
            blood_group=p["blood"],
            medical_history=p["history"]
        )
        db.add(pat)

    # 4. INITIAL APPOINTMENT
    tomorrow = date.today() + timedelta(days=1)
    apt1 = Appointment(
        id="apt-seed-01",
        patient_id="pat-01",
        doctor_id="doc-01",
        appointment_date=tomorrow,
        start_time=time(10, 0),
        end_time=time(10, 30),
        status="Confirmed",
        reason="Routine cardiovascular follow-up"
    )
    db.add(apt1)
    db.flush()

    # Payment for apt1
    pay1 = Payment(
        id=str(uuid.uuid4()),
        appointment_id=apt1.id,
        patient_id="pat-01",
        amount=1200.0,
        currency="INR",
        payment_mode="card",
        transaction_id="TXN-CARD-SEED-01",
        status="completed",
        receipt_number="REC-20260901-001"
    )
    db.add(pay1)

    # Notifications
    db.add(Notification(
        id=str(uuid.uuid4()),
        user_id="usr-pat-01",
        title="Appointment Confirmed",
        message=f"Your appointment with Dr. Sarah Jenkins on {tomorrow} at 10:00 AM has been confirmed.",
        type="confirmation"
    ))

    db.commit()
    logger.info("Seed data successfully populated!")

if __name__ == "__main__":
    from backend.app.database import SessionLocal, init_db
    init_db()
    db = SessionLocal()
    seed_database(db)
    db.close()
