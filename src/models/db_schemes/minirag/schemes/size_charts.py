from .rag_base import SQLAlchemyBase
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship


class SizeChart(SQLAlchemyBase):

    __tablename__ = "size_charts"

    size_chart_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False
    )

    size_label = Column(String, nullable=False)

    # Recommended body measurement ranges (cm)
    chest_min_cm = Column(Numeric(6, 1), nullable=True)
    chest_max_cm = Column(Numeric(6, 1), nullable=True)

    waist_min_cm = Column(Numeric(6, 1), nullable=True)
    waist_max_cm = Column(Numeric(6, 1), nullable=True)

    hip_min_cm = Column(Numeric(6, 1), nullable=True)
    hip_max_cm = Column(Numeric(6, 1), nullable=True)

    notes = Column(Text, nullable=True)

    product = relationship(
        "Product",
        back_populates="size_chart"
    )

    __table_args__ = (
        UniqueConstraint("product_id", "size_label"),
        CheckConstraint(
            "chest_min_cm <= chest_max_cm",
            name="ck_chest_range"
        ),
        CheckConstraint(
            "waist_min_cm <= waist_max_cm",
            name="ck_waist_range"
        ),
        CheckConstraint(
            "hip_min_cm <= hip_max_cm",
            name="ck_hip_range"
        ),
    )