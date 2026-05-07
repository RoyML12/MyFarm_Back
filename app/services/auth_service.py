import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import SessionResponse, TokenResponse
from app.schemas.user_schema import CurrentUserResponse

load_dotenv(Path(__file__).resolve().parent.parent.parent / '.env')

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-this-secret-key')
ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))
PASSWORD_RESET_EXPIRE_MINUTES = int(os.getenv('PASSWORD_RESET_EXPIRE_MINUTES', '30'))

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
security = HTTPBearer(auto_error=True)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def build_user_response(user) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=user.id,
        name=user.full_name,
        email=user.email,
        phone=user.phone,
        profileImageUrl=user.profile_image_url,
        isActive=bool(user.is_active),
        isAdmin=bool(user.is_admin),
        createdAt=user.created_at,
    )


def build_session_response(session) -> SessionResponse:
    return SessionResponse(
        id=session.id,
        deviceName=session.device_name,
        userAgent=session.user_agent,
        ipAddress=session.ip_address,
        isActive=bool(session.is_active),
        expiresAt=session.expires_at.isoformat() if session.expires_at else None,
        lastUsedAt=session.last_used_at.isoformat() if session.last_used_at else None,
        createdAt=session.created_at.isoformat() if session.created_at else None,
    )


def create_access_token(user_id: int, session_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        'sub': str(user_id),
        'sid': str(session_id),
        'type': 'access',
        'exp': expire,
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def create_password_reset_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def hash_password_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def create_login_response(*, user, session) -> TokenResponse:
    refresh_token = create_refresh_token()
    access_token = create_access_token(user.id, session.id)
    return access_token, refresh_token


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token inválido') from exc

    if payload.get('type') != 'access':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token inválido')
    return payload


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    payload = decode_access_token(credentials.credentials)
    user_id = int(payload.get('sub'))
    session_id = int(payload.get('sid'))

    repo = UserRepository(db)
    user = repo.get_user_by_id(user_id)
    session = repo.get_session_by_id(session_id)

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Usuario no autorizado')
    if not session or not session.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Sesión inválida o expirada')
    if session.expires_at <= datetime.utcnow():
        repo.revoke_session(session)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Sesión expirada')

    repo.touch_session(session)
    return user


def get_current_session(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    payload = decode_access_token(credentials.credentials)
    session_id = int(payload.get('sid'))
    repo = UserRepository(db)
    session = repo.get_session_by_id(session_id)
    if not session or not session.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Sesión inválida')
    return session
