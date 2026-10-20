from .rag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, Numeric,Text,String, Boolean, DateTime, func # func is used to get the current time
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

class Product(SQLAlchemyBase):

    __tablename__ = "products"

    product_id = Column(Integer,  primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Numeric(10,2), nullable=False) ## numeric(10,2) means 10 digits and 2 decimal places
    currency = Column(String, nullable=False, default="MAD")
    color = Column(String, nullable=False)
    material = Column(String, nullable=False)
    fit = Column(String, nullable=True)
    is_avtive = Column(Boolean, nullable=True)
    occasions = Column(JSONB, nullable=True)
    style = Column(JSONB, nullable=True)
    
    image_url = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    variants = relationship("ProductVariant", back_populates="product")
    search_index = relationship("ProductSearchIndex", back_populates="product")
    size_chart = relationship("SizeChart", back_populates="product",  cascade="all, delete-orphan")