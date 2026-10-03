import sys, os
sys.path.insert(0, os.path.abspath('.'))
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# 1. Verify all 8 doctors show in Find Doctors
docs = client.get('/api/doctors').json()
print(f"=== DOCTORS ({len(docs)}) ===")
for d in docs:
    name = d["user"]["full_name"]
    spec = d["specialization"]
    qual = d["qualification"]
    print(f"  {d['id']} | {name} | {spec} | {qual}")

# 2. Verify login credentials unchanged
print()
logins = [
    ("smit.gamit@demo.caresync.local", "Patient@12345", "patient"),
    ("aarav.mehta@demo.caresync.local", "Doctor@12345", "doctor"),
    ("admin@demo.caresync.local", "Admin@12345", "admin"),
]
for email, pw, role in logins:
    r = client.post("/api/auth/login", json={"email": email, "password": pw})
    status = "OK" if r.status_code == 200 else "FAIL"
    print(f"Login {role:8} ({email}): {status} ({r.status_code})")

# 3. Verify availability exists for all 8
print()
from backend.app.database import SessionLocal
from backend.app.models.appointment import DoctorAvailability
db = SessionLocal()
for i in range(1, 9):
    doc_id = f"doc-0{i}"
    count = db.query(DoctorAvailability).filter(DoctorAvailability.doctor_id == doc_id).count()
    print(f"  {doc_id}: {count} availability slots")
db.close()

# 4. Verify specialization filter
print()
cardio = client.get("/api/doctors", params={"specialization": "Cardiologist"}).json()
print(f"Cardiologist filter: {len(cardio)} result(s)")
ent = client.get("/api/doctors", params={"specialization": "ENT Specialist"}).json()
print(f"ENT Specialist filter: {len(ent)} result(s)")
gyno = client.get("/api/doctors", params={"specialization": "Gynecologist"}).json()
print(f"Gynecologist filter: {len(gyno)} result(s)")
