import sqlite3
from backend.app.core.security import verify_password
conn = sqlite3.connect('doctor_appointments.db')
rows = conn.execute("SELECT id, email, password_hash, is_active FROM users WHERE email='admin@hospital.com'").fetchall()
print(f"Found {len(rows)} users with email admin@hospital.com")
for r in rows:
    print(r)
