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
        email="admin@demo.caresync.local",
        password_hash=admin_pw,
        full_name="Hospital Administrator",
        role="admin",
        phone_number="+91 90000 00001",
        is_active=True
    )
    db.add(admin_user)

    # 2. DOCTORS (8 Indian demo doctors)
    doctors_info = [
        {
            "user_id": "usr-doc-01",
            "doc_id": "doc-01",
            "name": "Dr. Aarav Mehta",
            "email": "aarav.mehta@demo.caresync.local",
            "phone": "+91 98765 01001",
            "specialization": "Cardiologist",
            "qualification": "MBBS, MD (Medicine), DM (Cardiology)",
            "exp": 12,
            "address": "Heart & Vascular Centre, Ahmedabad, Gujarat",
            "fee": 1200.0,
            "bio": "Experienced cardiologist specializing in non-invasive cardiovascular treatments, preventative cardiac care, and heart failure management.",
            "rating": 5.0,
            "count": 28
        },
        {
            "user_id": "usr-doc-02",
            "doc_id": "doc-02",
            "name": "Dr. Priya Sharma",
            "email": "priya.sharma@demo.caresync.local",
            "phone": "+91 98765 01002",
            "specialization": "Pediatrician",
            "qualification": "MBBS, MD (Pediatrics)",
            "exp": 8,
            "address": "Children's Care Clinic, Vadodara, Gujarat",
            "fee": 800.0,
            "bio": "Compassionate pediatric specialist dedicated to child health, vaccinations, growth monitoring, and developmental wellbeing.",
            "rating": 5.0,
            "count": 35
        },
        {
            "user_id": "usr-doc-03",
            "doc_id": "doc-03",
            "name": "Dr. Rohan Patel",
            "email": "rohan.patel@demo.caresync.local",
            "phone": "+91 98765 01003",
            "specialization": "Dermatologist",
            "qualification": "MBBS, MD (Dermatology)",
            "exp": 9,
            "address": "Skin & Wellness Clinic, Ahmedabad, Gujarat",
            "fee": 900.0,
            "bio": "Specialist in clinical and cosmetic dermatology, acne therapies, eczema treatment, and skin health management.",
            "rating": 4.8,
            "count": 19
        },
        {
            "user_id": "usr-doc-04",
            "doc_id": "doc-04",
            "name": "Dr. Neha Shah",
            "email": "neha.shah@demo.caresync.local",
            "phone": "+91 98765 01004",
            "specialization": "General Physician",
            "qualification": "MBBS, MD (General Medicine)",
            "exp": 7,
            "address": "Shree Health Clinic, Surat, Gujarat",
            "fee": 600.0,
            "bio": "Experienced general physician focusing on routine check-ups, lifestyle diseases, diabetes, and hypertension management.",
            "rating": 4.7,
            "count": 14
        },
        {
            "user_id": "usr-doc-05",
            "doc_id": "doc-05",
            "name": "Dr. Kunal Desai",
            "email": "kunal.desai@demo.caresync.local",
            "phone": "+91 98765 01005",
            "specialization": "Neurologist",
            "qualification": "MBBS, MD (Medicine), DM (Neurology)",
            "exp": 11,
            "address": "NeuroCare Centre, Mumbai, Maharashtra",
            "fee": 1100.0,
            "bio": "Leading neurologist treating migraines, neurological disorders, epilepsy, and stroke rehabilitation.",
            "rating": 4.9,
            "count": 22
        },
        {
            "user_id": "usr-doc-06",
            "doc_id": "doc-06",
            "name": "Dr. Ananya Joshi",
            "email": "ananya.joshi@demo.caresync.local",
            "phone": "+91 98765 01006",
            "specialization": "Gynecologist",
            "qualification": "MBBS, MD (Obstetrics & Gynecology)",
            "exp": 10,
            "address": "Women's Care Hospital, Vadodara, Gujarat",
            "fee": 1000.0,
            "bio": "Dedicated gynecologist specializing in women's health, prenatal care, high-risk pregnancies, and minimally invasive surgeries.",
            "rating": 4.9,
            "count": 31
        },
        {
            "user_id": "usr-doc-07",
            "doc_id": "doc-07",
            "name": "Dr. Vivek Trivedi",
            "email": "vivek.trivedi@demo.caresync.local",
            "phone": "+91 98765 01007",
            "specialization": "Orthopedic Surgeon",
            "qualification": "MBBS, MS (Orthopedics)",
            "exp": 13,
            "address": "OrthoCare Hospital, Ahmedabad, Gujarat",
            "fee": 1000.0,
            "bio": "Skilled orthopedic surgeon specializing in joint replacement, sports injuries, fracture management, and spinal disorders.",
            "rating": 4.8,
            "count": 25
        },
        {
            "user_id": "usr-doc-08",
            "doc_id": "doc-08",
            "name": "Dr. Meera Iyer",
            "email": "meera.iyer@demo.caresync.local",
            "phone": "+91 98765 01008",
            "specialization": "ENT Specialist",
            "qualification": "MBBS, MS (ENT)",
            "exp": 8,
            "address": "ENT & Hearing Care Centre, Bengaluru, Karnataka",
            "fee": 750.0,
            "bio": "Experienced ENT specialist providing comprehensive care for ear, nose, and throat conditions including hearing disorders and sinus treatments.",
            "rating": 4.8,
            "count": 18
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
            "name": "Smit Gamit",
            "email": "smit.gamit@demo.caresync.local",
            "phone": "+91 98765 02001",
            "dob": date(1988, 4, 12),
            "gender": "Male",
            "blood": "O+",
            "history": "Mild hypertension, taking Losartan 25mg daily. No known drug allergies."
        },
        {
            "user_id": "usr-pat-02",
            "pat_id": "pat-02",
            "name": "Kavya Patel",
            "email": "kavya.patel@demo.caresync.local",
            "phone": "+91 98765 02002",
            "dob": date(1993, 9, 25),
            "gender": "Female",
            "blood": "A+",
            "history": "Asthma, seasonal pollen allergy. Uses salbutamol inhaler as needed."
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
        reason="Routine cardiovascular follow-up",
        consultation_fee_snapshot=1200.0
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
        message=f"Your appointment with Dr. Aarav Mehta on {tomorrow} at 10:00 AM has been confirmed.",
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
