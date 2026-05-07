from sqlalchemy import BigInteger, Column, DECIMAL, ForeignKey, String, Text, TIMESTAMP, text
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(BigInteger().with_variant(BigInteger, 'mysql'), primary_key=True, autoincrement=True)
    seller_id = Column(BigInteger().with_variant(BigInteger, 'mysql'), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    type_material = Column(String(50), nullable=False, index=True)
    breed = Column(String(100), nullable=False, index=True)
    origin = Column(String(50), nullable=False, server_default='Nacional', index=True)
    location = Column(String(150), nullable=False, index=True)
    price = Column(DECIMAL(12, 2), nullable=False, index=True)
    availability = Column(String(50), nullable=False, server_default='Disponible', index=True)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=False)
    pedigree = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, server_default='active', index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    seller = relationship('User', back_populates='products')
    certifications = relationship('ProductCertification', back_populates='product', cascade='all, delete-orphan')
    favorite_items = relationship('Favorite', back_populates='product', cascade='all, delete-orphan')
    conversations = relationship('Conversation', back_populates='product', cascade='all, delete-orphan')
