from sqlalchemy import BigInteger, Column, ForeignKey, TIMESTAMP, UniqueConstraint, text
from sqlalchemy.orm import relationship

from app.database import Base


class Conversation(Base):
    __tablename__ = 'conversations'
    __table_args__ = (UniqueConstraint('product_id', 'buyer_id', 'seller_id', name='uq_conversation_product_buyer_seller'),)

    id = Column(BigInteger().with_variant(BigInteger, 'mysql'), primary_key=True, autoincrement=True)
    product_id = Column(BigInteger().with_variant(BigInteger, 'mysql'), ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    buyer_id = Column(BigInteger().with_variant(BigInteger, 'mysql'), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    seller_id = Column(BigInteger().with_variant(BigInteger, 'mysql'), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    product = relationship('Product', back_populates='conversations')
    buyer = relationship('User', back_populates='buyer_conversations', foreign_keys=[buyer_id])
    seller_user = relationship('User', back_populates='seller_conversations', foreign_keys=[seller_id])
    messages = relationship('Message', back_populates='conversation', cascade='all, delete-orphan')
