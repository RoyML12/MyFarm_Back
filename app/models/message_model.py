from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Text, TIMESTAMP, text
from sqlalchemy.orm import relationship

from app.database import Base


class Message(Base):
    __tablename__ = 'messages'

    id = Column(BigInteger().with_variant(BigInteger, 'mysql'), primary_key=True, autoincrement=True)
    conversation_id = Column(BigInteger().with_variant(BigInteger, 'mysql'), ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    sender_id = Column(BigInteger().with_variant(BigInteger, 'mysql'), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, server_default=text('0'), index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    conversation = relationship('Conversation', back_populates='messages')
    sender = relationship('User', back_populates='sent_messages')
