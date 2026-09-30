import logging
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
    logger.warning("⚠️  Using local SQLite database. Set DATABASE_URL to a PostgreSQL URL for production use.")
else:
    logger.info(f"🗄️  Connecting to PostgreSQL database...")

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import backend.app.models  # ensure all models are registered with Base metadata
    Base.metadata.create_all(bind=engine)
    # Verify the connection by running a lightweight query
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_type = "SQLite" if DATABASE_URL.startswith("sqlite") else "PostgreSQL"
        logger.info(f"✅ Database connection verified ({db_type})")
    except Exception as exc:
        logger.error(f"❌ Database connection failed: {exc}")
        raise
