import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SessionResponse,
    TokenResponse,
)
from app.services.auth_service import (
    PASSWORD_RESET_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    build_session_response,
    build_user_response,
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    get_current_session,
    get_current_user,
    hash_password,
    hash_password_reset_token,
    hash_refresh_token,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/register', response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    existing = repo.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='El correo ya está registrado')

    user = repo.create_user(
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        phone=payload.phone,
    )

    refresh_token = create_refresh_token()
    session = repo.create_session(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        device_name='Registro Web',
        user_agent=request.headers.get('user-agent'),
        ip_address=request.client.host if request.client else None,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    access_token = create_access_token(user.id, session.id)
    return TokenResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        user=build_user_response(user),
    )


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_user_by_email(payload.email.lower())
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Correo o contraseña incorrectos')
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Usuario inactivo')

    refresh_token = create_refresh_token()
    session = repo.create_session(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        device_name=payload.deviceName or 'Web Browser',
        user_agent=request.headers.get('user-agent'),
        ip_address=request.client.host if request.client else None,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    access_token = create_access_token(user.id, session.id)

    return TokenResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        user=build_user_response(user),
    )


@router.post('/forgot-password', response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_user_by_email(payload.email.lower())

    generic_message = 'Si el correo existe, se generó un enlace para recuperar la contraseña.'

    if not user or not user.is_active:
        return ForgotPasswordResponse(message=generic_message)

    reset_token = create_password_reset_token()
    expires_at = datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)
    repo.create_password_reset_token(
        user_id=user.id,
        token_hash=hash_password_reset_token(reset_token),
        expires_at=expires_at,
    )

    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    reset_url = f'{frontend_url}/reset-password?token={reset_token}'

    print(f'[MyFarm Password Reset] {user.email}: {reset_url}')

    # MVP/desarrollo: se devuelve el token para poder probar sin servicio SMTP.
    # En producción lo correcto es enviar reset_url por correo y no exponer resetToken.
    return ForgotPasswordResponse(
        message=generic_message,
        resetToken=reset_token,
        resetUrl=reset_url,
    )


@router.post('/reset-password', response_model=ResetPasswordResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    reset_token = repo.get_password_reset_token_by_hash(hash_password_reset_token(payload.token))

    if not reset_token or reset_token.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='El enlace de recuperación no es válido')

    if reset_token.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='El enlace de recuperación expiró')

    user = repo.get_user_by_id(reset_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Usuario no válido')

    repo.update_user_password(user, hash_password(payload.password))
    repo.mark_password_reset_token_used(reset_token)
    repo.revoke_sessions_by_user(user.id)

    return ResetPasswordResponse(message='Contraseña actualizada correctamente. Inicia sesión nuevamente.')


@router.post('/refresh', response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    refresh_hash = hash_refresh_token(payload.refreshToken)
    session = repo.get_active_session_by_hash(refresh_hash)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token inválido')
    if session.expires_at <= datetime.utcnow():
        repo.revoke_session(session)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token expirado')

    user = repo.get_user_by_id(session.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Usuario no válido')

    new_refresh_token = create_refresh_token()
    repo.update_session_token(
        session,
        refresh_token_hash=hash_refresh_token(new_refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    access_token = create_access_token(user.id, session.id)

    return TokenResponse(
        accessToken=access_token,
        refreshToken=new_refresh_token,
        user=build_user_response(user),
    )


@router.post('/logout', response_model=LogoutResponse)
def logout(db_session=Depends(get_current_session), db: Session = Depends(get_db)):
    repo = UserRepository(db)
    current = repo.get_session_by_id(db_session.id)
    if current and current.is_active:
        repo.revoke_session(current)
    return LogoutResponse(message='Sesión cerrada correctamente')


@router.get('/me')
def me(current_user=Depends(get_current_user)):
    return build_user_response(current_user)


@router.get('/sessions', response_model=list[SessionResponse])
def list_sessions(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    repo = UserRepository(db)
    sessions = repo.list_sessions_by_user(current_user.id)
    return [build_session_response(item) for item in sessions]


@router.delete('/sessions/{session_id}', response_model=LogoutResponse)
def revoke_session(session_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    repo = UserRepository(db)
    session = repo.get_session_by_id(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Sesión no encontrada')
    repo.revoke_session(session)
    return LogoutResponse(message='Sesión revocada correctamente')
