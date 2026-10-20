from .rag_base import SQLAlchemyBase

from sqlalchemy import Column, Integer,String,ForeignKey ,UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
class ProductVariant(SQLAlchemyBase):

    __tablename__ = "variants"
    variant_product_id = Column(Integer,  primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, unique=True) 
    size = Column(String, nullable=False, unique=True),
    stock = Column(Integer, nullable=False, default=0)
    


    product = relationship("Product", back_populates="variants")

    __table_args__ = (
        UniqueConstraint("product_id", "size"),
        CheckConstraint("stock >= 0", name="ck_variant_stock"),
    )