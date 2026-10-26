from langchian_core.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy import select

class CheckStocktInput(BaseModel):
    product_id: int = Field(
        gt=0,
        description="ID of the product to check"
    )

    size: str | None = Field(
        default=None,
        description="Requested size, such as M, XL or XXL"
    )

def create_check_stock_tool(catalog_service):
    @tool("size_chart_tool",args_schema=CheckStocktInput)
    async def check_stock(
        product_id: int,
        size: float
        )->dict:
        
        """
        Check the current stock availability of a product.

        Use this when the customer asks whether a specific
        product or size is available.

        Requires a real product ID from the product catalog.
        """
        result = await catalog_service.check_stock(
            product_id=product_id,
            size=size
        )

        return result
    
    return check_stock
        