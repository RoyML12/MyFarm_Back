from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, TIMESTAMP, text
from sqlalchemy.orm import relationship

from app.database import Base


class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'

    id = Column(BigInteger().with_variant(BigInteger, 'mysql'), primary_key=True, autoincrement=True)
    user_id = Column(BigInteger().with_variant(BigInteger, 'mysql'), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    user = relationship('User', back_populates='password_reset_tokens')
