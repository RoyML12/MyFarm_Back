from sqlalchemy import BigInteger, Boolean, Column, String, TIMESTAMP, text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger().with_variant(BigInteger, 'mysql'), primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))
    is_admin = Column(Boolean, nullable=False, server_default=text('0'))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    sessions = relationship('UserSession', back_populates='user', cascade='all, delete-orphan')
    products = relationship('Product', back_populates='seller', cascade='all, delete-orphan')
    favorite_items = relationship('Favorite', back_populates='user', cascade='all, delete-orphan')
    buyer_conversations = relationship('Conversation', back_populates='buyer', foreign_keys='Conversation.buyer_id')
    seller_conversations = relationship('Conversation', back_populates='seller_user', foreign_keys='Conversation.seller_id')
    sent_messages = relationship('Message', back_populates='sender')
    password_reset_tokens = relationship('PasswordResetToken', back_populates='user', cascade='all, delete-orphan')
