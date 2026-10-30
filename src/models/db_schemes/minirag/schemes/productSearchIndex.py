from pydantic import BaseModel

from .rag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer,Computed,String, Index, ForeignKey, func # func is used to get the current time
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector
import uuid
class ProductSearchIndex(SQLAlchemyBase):

    __tablename__ = "products_search_index"

    product_id = Column(Integer,ForeignKey("products.product_id") ,primary_key=True)

    searchable_text = Column(String, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    tsv = Column(TSVECTOR, 
        Computed(
        "to_tsvector('english'::regconfig, "
        "coalesce(searchable_text, ''))",
        persisted=True
    ))

    
    product = relationship("Product",back_populates="search_index", uselist=False) ## uselist means it will be a single object

    __table_args__ = (
        Index(
            "idx_product_search_tsv",
            "tsv",
            postgresql_using="gin"
        ),
    )

# Index(
#     "idx_product_embedding_hnsw",
#     "embedding",
#     postgresql_using="hnsw",
#     postgresql_ops={"embedding": "vector_cosine_ops"}
# )

class RetrievedProduct(BaseModel):
    text: str 
    score: float
    product_id: int | None = None
    price: float | None = None
    color: str | None = None
    
