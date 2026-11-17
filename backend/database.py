import os
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Database File Location (Always absolute path inside backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "stockmaster.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

# 2. SQLite Engine Configuration
# check_same_thread=False allows FastAPI multithreaded requests to use SQLite safely
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 3. Enforce SQLite Foreign Key Constraints
# By default, SQLite has foreign keys DISABLED. We enable it on every connection.
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# 4. Session Maker Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Declarative Base for ORM Models
Base = declarative_base()

# 6. Database Dependency for API Routes
def get_db():
    """
    FastAPI dependency that yields a database session per request
    and guarantees it is closed when the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
