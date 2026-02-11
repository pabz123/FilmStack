"""
Simple authentication system for Movie Library
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
import secrets
import hashlib

from backend.database import Base, SessionLocal, engine

router = APIRouter()
security = HTTPBasic()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Integer, default=0)


# Create users table
Base.metadata.create_all(bind=engine)


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    """Verify user credentials"""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    password_hash = hash_password(credentials.password)
    if not secrets.compare_digest(user.password_hash, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user


@router.post("/register")
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if this is the first user (make admin)
    user_count = db.query(User).count()
    is_admin = 1 if user_count == 0 else 0
    
    # Create user
    user = User(
        username=username,
        password_hash=hash_password(password),
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    
    return {"message": "User created successfully", "is_admin": bool(is_admin)}


@router.get("/me")
def get_current_user(user: User = Depends(verify_credentials)):
    """Get current user info"""
    return {
        "id": user.id,
        "username": user.username,
        "is_admin": bool(user.is_admin)
    }


@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    user: User = Depends(verify_credentials),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify old password
    if hash_password(old_password) != user.password_hash:
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    # Update password
    user.password_hash = hash_password(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
