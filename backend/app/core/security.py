from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings

# Password & PIN Hashing Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generates a secure bcrypt hash for a password."""
    return pwd_context.hash(password)

def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """Verifies a 4-8 digit customer gallery PIN against the stored hash."""
    return pwd_context.verify(plain_pin, hashed_pin)

def hash_pin(pin: str) -> str:
    """Hashes a gallery PIN securely."""
    return pwd_context.hash(pin)

def create_access_token(subject: Union[str, int], role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT access token for authenticated users (ADMIN / TEAM_MEMBER)."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "user_access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a user JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "user_access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def create_gallery_access_token(gallery_id: str, slug: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a short-lived signed JWT gallery access token after successful PIN verification.
    This token is strictly gallery-scoped.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.GALLERY_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "gallery_id": str(gallery_id),
        "slug": slug,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "gallery_access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.GALLERY_JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_gallery_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a customer gallery access token."""
    try:
        payload = jwt.decode(token, settings.GALLERY_JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "gallery_access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid gallery token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Gallery session expired. Please re-enter PIN.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid gallery access token")
