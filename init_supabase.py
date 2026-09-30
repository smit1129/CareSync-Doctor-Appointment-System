import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def main():
    # Load .env file
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url or "PASTE_YOUR_SUPABASE" in db_url:
        print("ERROR: DATABASE_URL is not properly configured in .env")
        sys.exit(1)
        
    print(f"Connecting to database...")
    
    # We disable echo to avoid printing sensitive data or huge logs
    engine = create_engine(db_url, echo=False)
    
    try:
        with engine.begin() as conn:
            # 1. Execute Schema
            print("Applying database/schema.sql...")
            with open("database/schema.sql", "r", encoding="utf-8") as f:
                schema_sql = f.read()
                # Split by statements or just execute the whole block
                # SQLAlchemy text() with multiple statements can sometimes be tricky with some drivers,
                # but psycopg2 handles it well if we just pass the raw string.
                conn.execute(text(schema_sql))
            print("Schema applied successfully.")
            
            # 2. Execute Seed Data
            print("Applying database/seed.sql...")
            with open("database/seed.sql", "r", encoding="utf-8") as f:
                seed_sql = f.read()
                conn.execute(text(seed_sql))
            print("Seed data applied successfully.")
            
    except Exception as e:
        print(f"ERROR executing SQL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
