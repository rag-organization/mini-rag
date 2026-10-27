from langchain_core.tools import tool
from pydantic import BaseModel, Field
class BuildOutfitInput(BaseModel):
    occasion: str = Field(
        min_length=1,
        description="Occasion such as wedding, business, or casual"
    )

    categories: list[str] = Field(
        default_factory=lambda: ["shirt", "trousers", "shoes"],
        description="Product categories required for the outfit"
    )

    max_budget: float | None = Field(
        default=None,
        gt=0,
        description="Maximum total outfit budget in MAD"
    )

    sizes: dict[str, str] | None = Field(
        default=None,
        description=(
            "Requested size per category, for example "
            "{'shirt': 'XL', 'trousers': 'L', 'shoes': '43'}"
        )
    )

def create_outfit_tool(outfit_service):
    @tool("build_outfit_tool",args_schema=BuildOutfitInput)
    async def build_outfit(
        occasion: str,
        categories: list[str] | None = None,
        max_budget: float | None = None,
        sizes: dict[str, str] | None = None
    )->dict:
        """
        Build a complete outfit using real products from the store.

        Use when the customer wants a coordinated outfit for
        an occasion, possibly with a budget or size requirements.

        Return only products supported by catalog search.
        """

        return await outfit_service.build_outfit(
                occasion=occasion, 
                categories=categories, 
                max_budget=max_budget, 
                sizes=sizes)

    return build_outfit