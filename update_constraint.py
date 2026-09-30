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
            # Drop the old constraint. The constraint name is usually generated, but we can drop it by constraint name or recreate the table if needed.
            # Actually, standard postgres lets us drop and add constraints.
            # Let's find the constraint name.
            res = conn.execute(text("SELECT conname FROM pg_constraint WHERE conrelid = 'appointments'::regclass AND contype = 'c' AND pg_get_constraintdef(oid) LIKE '%status%';"))
            conname = res.scalar()
            
            if conname:
                print(f"Dropping constraint: {conname}")
                conn.execute(text(f"ALTER TABLE appointments DROP CONSTRAINT {conname}"))
            
            print("Adding new constraint...")
            conn.execute(text("ALTER TABLE appointments ADD CONSTRAINT appointments_status_check CHECK (status IN ('Requested', 'Payment Pending', 'Confirmed', 'Rejected', 'Cancelled', 'Rescheduled', 'Completed'))"))
            print("Database updated successfully.")
    except Exception as e:
        print(f"Error updating DB: {e}")

if __name__ == "__main__":
    main()
