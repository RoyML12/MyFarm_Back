from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user_model import User
from app.models.user_session_model import UserSession
from app.models.password_reset_token_model import PasswordResetToken


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, *, name: str, email: str, password_hash: str, phone: str | None = None):
        user = User(full_name=name, email=email, password_hash=password_hash, phone=phone)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_session(self, *, user_id: int, refresh_token_hash: str, device_name: str | None, user_agent: str | None, ip_address: str | None, expires_at: datetime):
        session = UserSession(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            device_name=device_name,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
            last_used_at=datetime.utcnow(),
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session_by_id(self, session_id: int):
        return self.db.query(UserSession).filter(UserSession.id == session_id).first()

    def get_active_session_by_hash(self, refresh_token_hash: str):
        return (
            self.db.query(UserSession)
            .filter(UserSession.refresh_token_hash == refresh_token_hash, UserSession.is_active.is_(True))
            .first()
        )

    def list_sessions_by_user(self, user_id: int):
        return (
            self.db.query(UserSession)
            .filter(UserSession.user_id == user_id)
            .order_by(UserSession.created_at.desc())
            .all()
        )

    def update_session_token(self, session: UserSession, refresh_token_hash: str, expires_at: datetime):
        session.refresh_token_hash = refresh_token_hash
        session.expires_at = expires_at
        session.last_used_at = datetime.utcnow()
        session.revoked_at = None
        session.is_active = True
        self.db.commit()
        self.db.refresh(session)
        return session

    def touch_session(self, session: UserSession):
        session.last_used_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session

    def revoke_session(self, session: UserSession):
        session.is_active = False
        session.revoked_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_user_password(self, user: User, password_hash: str):
        user.password_hash = password_hash
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_password_reset_token(self, *, user_id: int, token_hash: str, expires_at: datetime):
        reset_token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(reset_token)
        self.db.commit()
        self.db.refresh(reset_token)
        return reset_token

    def get_password_reset_token_by_hash(self, token_hash: str):
        return (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == token_hash)
            .first()
        )

    def mark_password_reset_token_used(self, reset_token: PasswordResetToken):
        reset_token.used_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(reset_token)
        return reset_token

    def revoke_sessions_by_user(self, user_id: int):
        sessions = (
            self.db.query(UserSession)
            .filter(UserSession.user_id == user_id, UserSession.is_active.is_(True))
            .all()
        )
        for session in sessions:
            session.is_active = False
            session.revoked_at = datetime.utcnow()
        self.db.commit()
        return sessions
