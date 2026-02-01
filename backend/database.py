import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load from parent directory
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)
except ImportError:
    pass

DATABASE_PATH = os.getenv("DATABASE_PATH", "movies.db")
# Use absolute path for database
if not os.path.isabs(DATABASE_PATH):
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_PATH)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

print(f"Database URL: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class - simple style
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    # Import all models here so they register with Base
    from models import Movie, Series, Season, Episode
    from auth import User
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
