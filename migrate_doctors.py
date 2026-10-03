"""
Migration script: Updates existing 5 doctors to Indian demo data,
adds 3 new doctors to reach 8 total Indian doctors.
Also fixes stale patient data (Alice Smith → Kavya Patel).
Does NOT modify authentication, passwords, security, or appointment workflow.
"""
import sys, os, uuid
from datetime import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from backend.app.database import SessionLocal, init_db
from backend.app.models.user import User, Doctor
from backend.app.models.appointment import DoctorAvailability
from backend.app.core.security import hash_password

# The 8 final Indian doctors
DOCTORS = [
    {
        "user_id": "usr-doc-01", "doc_id": "doc-01",
        "name": "Dr. Aarav Mehta",
        "email": "aarav.mehta@demo.caresync.local",
        "phone": "+91 98765 01001",
        "specialization": "Cardiologist",
        "qualification": "MBBS, MD (Medicine), DM (Cardiology)",
        "exp": 12,
        "address": "Heart & Vascular Centre, Ahmedabad, Gujarat",
        "fee": 1200.0,
        "bio": "Experienced cardiologist specializing in non-invasive cardiovascular treatments, preventative cardiac care, and heart failure management.",
        "rating": 5.0, "count": 28
    },
    {
        "user_id": "usr-doc-02", "doc_id": "doc-02",
        "name": "Dr. Priya Sharma",
        "email": "priya.sharma@demo.caresync.local",
        "phone": "+91 98765 01002",
        "specialization": "Pediatrician",
        "qualification": "MBBS, MD (Pediatrics)",
        "exp": 8,
        "address": "Children's Care Clinic, Vadodara, Gujarat",
        "fee": 800.0,
        "bio": "Compassionate pediatric specialist dedicated to child health, vaccinations, growth monitoring, and developmental wellbeing.",
        "rating": 5.0, "count": 35
    },
    {
        "user_id": "usr-doc-03", "doc_id": "doc-03",
        "name": "Dr. Rohan Patel",
        "email": "rohan.patel@demo.caresync.local",
        "phone": "+91 98765 01003",
        "specialization": "Dermatologist",
        "qualification": "MBBS, MD (Dermatology)",
        "exp": 9,
        "address": "Skin & Wellness Clinic, Ahmedabad, Gujarat",
        "fee": 900.0,
        "bio": "Specialist in clinical and cosmetic dermatology, acne therapies, eczema treatment, and skin health management.",
        "rating": 4.8, "count": 19
    },
    {
        "user_id": "usr-doc-04", "doc_id": "doc-04",
        "name": "Dr. Neha Shah",
        "email": "neha.shah@demo.caresync.local",
        "phone": "+91 98765 01004",
        "specialization": "General Physician",
        "qualification": "MBBS, MD (General Medicine)",
        "exp": 7,
        "address": "Shree Health Clinic, Surat, Gujarat",
        "fee": 600.0,
        "bio": "Experienced general physician focusing on routine check-ups, lifestyle diseases, diabetes, and hypertension management.",
        "rating": 4.7, "count": 14
    },
    {
        "user_id": "usr-doc-05", "doc_id": "doc-05",
        "name": "Dr. Kunal Desai",
        "email": "kunal.desai@demo.caresync.local",
        "phone": "+91 98765 01005",
        "specialization": "Neurologist",
        "qualification": "MBBS, MD (Medicine), DM (Neurology)",
        "exp": 11,
        "address": "NeuroCare Centre, Mumbai, Maharashtra",
        "fee": 1100.0,
        "bio": "Leading neurologist treating migraines, neurological disorders, epilepsy, and stroke rehabilitation.",
        "rating": 4.9, "count": 22
    },
    {
        "user_id": "usr-doc-06", "doc_id": "doc-06",
        "name": "Dr. Ananya Joshi",
        "email": "ananya.joshi@demo.caresync.local",
        "phone": "+91 98765 01006",
        "specialization": "Gynecologist",
        "qualification": "MBBS, MD (Obstetrics & Gynecology)",
        "exp": 10,
        "address": "Women's Care Hospital, Vadodara, Gujarat",
        "fee": 1000.0,
        "bio": "Dedicated gynecologist specializing in women's health, prenatal care, high-risk pregnancies, and minimally invasive surgeries.",
        "rating": 4.9, "count": 31
    },
    {
        "user_id": "usr-doc-07", "doc_id": "doc-07",
        "name": "Dr. Vivek Trivedi",
        "email": "vivek.trivedi@demo.caresync.local",
        "phone": "+91 98765 01007",
        "specialization": "Orthopedic Surgeon",
        "qualification": "MBBS, MS (Orthopedics)",
        "exp": 13,
        "address": "OrthoCare Hospital, Ahmedabad, Gujarat",
        "fee": 1000.0,
        "bio": "Skilled orthopedic surgeon specializing in joint replacement, sports injuries, fracture management, and spinal disorders.",
        "rating": 4.8, "count": 25
    },
    {
        "user_id": "usr-doc-08", "doc_id": "doc-08",
        "name": "Dr. Meera Iyer",
        "email": "meera.iyer@demo.caresync.local",
        "phone": "+91 98765 01008",
        "specialization": "ENT Specialist",
        "qualification": "MBBS, MS (ENT)",
        "exp": 8,
        "address": "ENT & Hearing Care Centre, Bengaluru, Karnataka",
        "fee": 750.0,
        "bio": "Experienced ENT specialist providing comprehensive care for ear, nose, and throat conditions including hearing disorders and sinus treatments.",
        "rating": 4.8, "count": 18
    },
]


def migrate():
    init_db()
    db = SessionLocal()
    doc_pw = hash_password("Doctor@12345")

    try:
        for d in DOCTORS:
            # Check if user already exists
            user = db.query(User).filter(User.id == d["user_id"]).first()
            doctor = db.query(Doctor).filter(Doctor.id == d["doc_id"]).first()

            if user:
                # Update existing user
                user.full_name = d["name"]
                user.email = d["email"]
                user.phone_number = d["phone"]
                user.role = "doctor"
                user.is_active = True
                print(f"  [UPDATE] User {d['user_id']}: {d['name']}")
            else:
                # Create new user
                user = User(
                    id=d["user_id"],
                    email=d["email"],
                    password_hash=doc_pw,
                    full_name=d["name"],
                    role="doctor",
                    phone_number=d["phone"],
                    is_active=True
                )
                db.add(user)
                db.flush()
                print(f"  [CREATE] User {d['user_id']}: {d['name']}")

            if doctor:
                # Update existing doctor
                doctor.user_id = d["user_id"]
                doctor.specialization = d["specialization"]
                doctor.qualification = d["qualification"]
                doctor.experience_years = d["exp"]
                doctor.clinic_address = d["address"]
                doctor.consultation_fee = d["fee"]
                doctor.bio = d["bio"]
                doctor.rating_avg = d["rating"]
                doctor.rating_count = d["count"]
                print(f"  [UPDATE] Doctor {d['doc_id']}: {d['specialization']}")
            else:
                # Create new doctor
                doctor = Doctor(
                    id=d["doc_id"],
                    user_id=d["user_id"],
                    specialization=d["specialization"],
                    qualification=d["qualification"],
                    experience_years=d["exp"],
                    clinic_address=d["address"],
                    consultation_fee=d["fee"],
                    bio=d["bio"],
                    rating_avg=d["rating"],
                    rating_count=d["count"]
                )
                db.add(doctor)
                print(f"  [CREATE] Doctor {d['doc_id']}: {d['specialization']}")

                # Add Mon-Sat availability 09:00-17:00 for new doctors
                for day in range(6):
                    avail = DoctorAvailability(
                        id=str(uuid.uuid4()),
                        doctor_id=d["doc_id"],
                        day_of_week=day,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        slot_duration_minutes=30,
                        is_active=True
                    )
                    db.add(avail)
                print(f"  [CREATE] Availability for {d['doc_id']} (Mon-Sat 09:00-17:00)")

        # Fix patient Alice Smith -> Kavya Patel
        alice_user = db.query(User).filter(User.id == "usr-pat-02").first()
        if alice_user and alice_user.full_name == "Alice Smith":
            alice_user.full_name = "Kavya Patel"
            alice_user.email = "kavya.patel@demo.caresync.local"
            alice_user.phone_number = "+91 98765 02002"
            print(f"  [UPDATE] Patient usr-pat-02: Alice Smith -> Kavya Patel")

        # Fix admin phone number
        admin_user = db.query(User).filter(User.id == "usr-admin-01").first()
        if admin_user and admin_user.phone_number and admin_user.phone_number.startswith("+1"):
            admin_user.phone_number = "+91 90000 00001"
            print(f"  [UPDATE] Admin phone -> +91 90000 00001")

        # Fix patient Smit phone number
        smit_user = db.query(User).filter(User.id == "usr-pat-01").first()
        if smit_user and smit_user.phone_number and smit_user.phone_number.startswith("+1"):
            smit_user.phone_number = "+91 98765 02001"
            print(f"  [UPDATE] Patient Smit phone -> +91 98765 02001")

        db.commit()
        print("\n=== Migration complete ===")

        # Verify
        count = db.query(Doctor).count()
        print(f"\nTotal doctors in DB: {count}")
        all_docs = db.query(Doctor).all()
        for doc in all_docs:
            u = db.query(User).filter(User.id == doc.user_id).first()
            print(f"  {doc.id} | {u.full_name} | {doc.specialization} | {doc.qualification}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
