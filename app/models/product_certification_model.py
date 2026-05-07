from sqlalchemy import BigInteger, Boolean, Column, Date, ForeignKey, String, TIMESTAMP, text
from sqlalchemy.orm import relationship

from app.database import Base


class ProductCertification(Base):
    __tablename__ = 'product_certifications'

    id = Column(BigInteger().with_variant(BigInteger, 'mysql'), primary_key=True, autoincrement=True)
    product_id = Column(BigInteger().with_variant(BigInteger, 'mysql'), ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    certification_name = Column(String(150), nullable=False, index=True)
    document_url = Column(String(500), nullable=True)
    issued_by = Column(String(150), nullable=True)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    is_verified = Column(Boolean, nullable=False, server_default=text('0'), index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    product = relationship('Product', back_populates='certifications')
