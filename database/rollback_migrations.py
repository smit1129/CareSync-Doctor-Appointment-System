import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def rollback_migrations():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url or "PASTE_YOUR_SUPABASE" in db_url:
        print("ERROR: DATABASE_URL is not properly configured in .env")
        sys.exit(1)

    print("Connecting to database...")
    engine = create_engine(db_url, echo=False)

    rollback_file = os.path.join(
        os.path.dirname(__file__), "migrations", "001_rollback_rls_and_secure_privileges.sql"
    )

    if not os.path.exists(rollback_file):
        print(f"ERROR: Rollback file not found: {rollback_file}")
        sys.exit(1)

    with open(rollback_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print(f"Applying rollback: {os.path.basename(rollback_file)}...")
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            lines = [l for l in stmt.split("\n") if not l.strip().startswith("--")]
            clean_stmt = "\n".join(lines).strip()
            if not clean_stmt:
                continue
            conn.execute(text(clean_stmt))

    print("[SUCCESS] Rollback applied successfully!")

if __name__ == "__main__":
    rollback_migrations()
