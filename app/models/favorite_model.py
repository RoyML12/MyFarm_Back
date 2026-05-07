from sqlalchemy import BigInteger, Column, ForeignKey, TIMESTAMP, UniqueConstraint, text
from sqlalchemy.orm import relationship

from app.database import Base


class Favorite(Base):
    __tablename__ = 'favorites'
    __table_args__ = (UniqueConstraint('user_id', 'product_id', name='uq_favorites_user_product'),)

    id = Column(BigInteger().with_variant(BigInteger, 'mysql'), primary_key=True, autoincrement=True)
    user_id = Column(BigInteger().with_variant(BigInteger, 'mysql'), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(BigInteger().with_variant(BigInteger, 'mysql'), ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    user = relationship('User', back_populates='favorite_items')
    product = relationship('Product', back_populates='favorite_items')
