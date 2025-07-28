import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Support both native and Docker deployments
# Use data directory for database persistence
if os.path.exists('/app/data'):
    # Docker environment - /app/data is mounted from ./backend/data
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:////app/data/posting_board_uuid.db')
else:
    # Native environment - use backend/data directory
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{data_dir}/posting_board_uuid.db')
# For SQLite, use StaticPool to avoid isolation issues
from sqlalchemy.pool import StaticPool
if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        DATABASE_URL, 
        echo=False,  # Turn off SQL logging for production
        connect_args={'check_same_thread': False},
        poolclass=StaticPool
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database - now handled by database_uuid_init.py"""
    from models import Base
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_session():
    return SessionLocal()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")