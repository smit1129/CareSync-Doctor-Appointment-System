import logging
from pathlib import Path
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

# Safety guard: if the .env DATABASE_URL is still a placeholder, abort early with a clear message
if "PASTE_YOUR_SUPABASE" in DATABASE_URL:
    raise RuntimeError(
        "\n\n⛔  DATABASE_URL is not configured.\n"
        "  Open the .env file in the project root and replace 'PASTE_YOUR_SUPABASE_SESSION_POOLER_URL_HERE'\n"
        "  with your actual Supabase Session Pooler connection string.\n"
        "  Example:\n"
        "    DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-ap-south-1.pooler.supabase.com:5432/postgres\n"
        "  Or set DATABASE_URL=sqlite:///./doctor_appointments.db to use local SQLite instead.\n"
    )

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    logger.warning("Using local SQLite database. Set DATABASE_URL to a PostgreSQL URL for production use.")

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    # PostgreSQL pool settings (ignored for SQLite)
    pool_pre_ping=True,
)

# Enable foreign keys and WAL mode for SQLite only
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

EXPECTED_PUBLIC_TABLES = [
    "users", "doctors", "patients", "doctor_availabilities",
    "appointments", "payments", "notifications",
    "feedback_ratings", "password_resets"
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_postgres_security():
    """
    Verifies that Row Level Security (RLS) is enabled on all 9 public tables and
    that anon and authenticated roles have no direct table privileges.
    This check is strictly read-only and performs NO DDL or schema alterations.
    Raises RuntimeError if any check fails to prevent silent false-positives.
    """
    with engine.connect() as conn:
        # 1. Verify RLS is enabled on all expected tables
        rls_query = text("""
            SELECT c.relname, c.relrowsecurity
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relkind = 'r'
              AND c.relname = ANY(:tables);
        """)
        rows = conn.execute(rls_query, {"tables": EXPECTED_PUBLIC_TABLES}).fetchall()
        rls_map = {r[0]: r[1] for r in rows}

        missing_tables = [t for t in EXPECTED_PUBLIC_TABLES if t not in rls_map]
        if missing_tables:
            raise RuntimeError(
                f"Database security verification failed: missing public tables: {missing_tables}. "
                "Run migrations or schema setup first."
            )

        disabled_rls = [t for t in EXPECTED_PUBLIC_TABLES if not rls_map.get(t, False)]
        if disabled_rls:
            raise RuntimeError(
                f"Database security verification failed: RLS is disabled on: {disabled_rls}. "
                "Please run 'python database/apply_migrations.py' before starting the application."
            )

        # 2. Verify anon and authenticated roles have no table privileges
        grants_query = text("""
            SELECT DISTINCT table_name, grantee, privilege_type
            FROM information_schema.role_table_grants
            WHERE table_schema = 'public'
              AND grantee IN ('anon', 'authenticated')
              AND table_name = ANY(:tables);
        """)
        grants_rows = conn.execute(grants_query, {"tables": EXPECTED_PUBLIC_TABLES}).fetchall()
        if grants_rows:
            violations = [f"{r[0]} ({r[1]}: {r[2]})" for r in grants_rows]
            raise RuntimeError(
                f"Database security verification failed: unexpected table grants to anon/authenticated: {violations}. "
                "Please run 'python database/apply_migrations.py' before starting the application."
            )

    logger.info("PostgreSQL Row Level Security (RLS) verified: all public tables secured.")

def apply_postgres_security():
    """
    Applies migration 001_enable_rls_and_secure_privileges.sql to enable RLS
    and revoke anon/authenticated privileges. Intended for migration runners
    and test fixtures, NOT for routine application startup.
    """
    migration_file = Path(__file__).resolve().parents[2] / "database" / "migrations" / "001_enable_rls_and_secure_privileges.sql"
    if not migration_file.exists():
        raise FileNotFoundError(f"Migration file not found: {migration_file}")

    with open(migration_file, "r", encoding="utf-8") as f:
        sql_content = f.read()
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            lines = [l for l in stmt.split("\n") if not l.strip().startswith("--")]
            clean_stmt = "\n".join(lines).strip()
            if clean_stmt:
                conn.execute(text(clean_stmt))

# Backwards compatibility alias
_apply_postgres_security = apply_postgres_security

def init_db(apply_security: bool = False):
    """
    Initializes database schema.
    By default (apply_security=False), strictly performs read-only security
    verification on PostgreSQL and avoids unexpected production schema changes.
    """
    import backend.app.models  # ensure all models are registered with Base metadata
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_type = "SQLite" if DATABASE_URL.startswith("sqlite") else "PostgreSQL"
        logger.info(f"Database connection verified ({db_type})")

        if engine.name == "postgresql":
            if apply_security:
                apply_postgres_security()
            verify_postgres_security()
        else:
            logger.warning("Running on SQLite. Row Level Security (RLS) is only enforced on PostgreSQL.")
    except Exception as exc:
        logger.error(f"Database initialization failed: {exc}")
        raise
