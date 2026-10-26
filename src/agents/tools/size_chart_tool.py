from langchian_core.tools import tool
from pydantic import BaseModel, Field
from models.db_schemes.minirag.schemes import SizeChart
from sqlalchemy import select
from services.CatalogService import CatalogToolsService
class SizeChartInput(BaseModel):
    product_id= Field(..., description="jdjd")
    chest_cm = Field


def create_get_size_chart_tool(catalog_service):
    @tool("size_chart_tool",args_schema=SizeChartInput)
    async def recommend_size(
        product_id: int,
        chest_cm: float | None = None,
        waist_cm: float | None = None,
        hip_cm: float | None = None
        )->dict:
        """
        Recommend clothing sizes from the actual product size chart.

        Use when the customer asks which size may fit them.
        Never invent size measurements or guarantee fit.
        """
        result = await catalog_service.recommend_size(
            product_id=product_id,
            chest_cm=chest_cm,
            waist_cm=waist_cm,
            hip_cm=hip_cm
        )

        return result
    
    return recommend_size
        