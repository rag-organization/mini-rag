from pydantic import BaseModel, Field
from decimal import Decimal


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    brand: str = Field(min_length=1)
    category: str = Field(min_length=1)

    price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2
    )

    currency: str = "MAD"
    color: str
    material: str
    fit: str | None = None
    is_avtive: bool | None = None

    occasions: list[str] | None = None
    style: list[str] | None = None

    image_url: str
    description: str

class SearchProduct(BaseModel):
    query: str
    limit: int = 5
    filters: dict | None