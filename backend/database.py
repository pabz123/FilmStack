import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from backend.config import DATABASE_URL, DATABASE_PATH

print(f"Database URL: {DATABASE_URL}")
print(f"Database Path: {DATABASE_PATH}")

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
