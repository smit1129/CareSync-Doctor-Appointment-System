"""
Diagnostic script — checks whether demo users exist in the database and validates
password verification works end-to-end.
NEVER prints password hashes or secrets.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from backend.app.database import SessionLocal, init_db, DATABASE_URL
from backend.app.models.user import User
from backend.app.core.security import verify_password, hash_password

DEMO_ACCOUNTS = [
    ("admin@demo.caresync.local",        "Admin@12345",   "admin"),
    ("aarav.mehta@demo.caresync.local",  "Doctor@12345",  "doctor"),
    ("smit.gamit@demo.caresync.local",   "Patient@12345", "patient"),
]

def run_diagnostics():
    db_type = "SQLite" if DATABASE_URL.startswith("sqlite") else "PostgreSQL"
    print(f"\n=== AUTH DIAGNOSTICS ===")
    print(f"Database type : {db_type}")
    print()

    # Ensure tables exist
    try:
        init_db()
    except Exception as e:
        print(f"[ERROR] init_db() failed: {e}")
        return

    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        print(f"Total users in DB : {total_users}")
        print()

        for email, plaintext_pw, expected_role in DEMO_ACCOUNTS:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                print(f"[MISSING] {email}  — user does NOT exist in the database")
                continue

            has_hash = bool(user.password_hash)
            role_ok  = user.role == expected_role
            active   = user.is_active
            pw_ok    = verify_password(plaintext_pw, user.password_hash) if has_hash else False

            status = "OK" if (has_hash and role_ok and active and pw_ok) else "FAIL"
            print(f"[{status}] {email}")
            print(f"       role      : {user.role}  (expected: {expected_role})  {'pass' if role_ok else 'FAIL'}")
            print(f"       is_active : {active}  {'pass' if active else 'FAIL'}")
            print(f"       hash_present : {has_hash}  {'pass' if has_hash else 'FAIL'}")
            print(f"       password_ok  : {pw_ok}  {'pass' if pw_ok else 'FAIL'}")
            print()

        # Self-test: ensure verify_password round-trips correctly
        test_hash = hash_password("TestPass123")
        round_trip = verify_password("TestPass123", test_hash)
        print(f"bcrypt round-trip self-test : {'PASS' if round_trip else 'FAIL'}")

    finally:
        db.close()

if __name__ == "__main__":
    run_diagnostics()
