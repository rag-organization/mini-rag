from langchain_core.tools import tool
## search knowledge base from rag
from pydantic import BaseModel, Field
class ProductSearchInput(BaseModel):
    query: str = Field(
        description="Product name or natural-language shopping request"
    )
    filters: dict = Field(
        description="""optional dictionary of structured search constraints, such as category, color, size, max_price, brand.
        for example : {"category": "Men / T-Shirts", "color": "White", "size": "M", "max_price": 50.0, "brand": "Casa Essentials"}""",
    )


def create_product_search_tool(catalog_controller):

    @tool("product_search_tool",
        args_schema=ProductSearchInput
        )
    async def search_products(query:str, filters):
        """
        Search the store's clothing catalog.
        Use this tool when a customer wants to discover
        products, such as shirts, jackets, trousers,
        or clothing suitable for an occasion.
        Supports semantic search, keyword search,
        and structured product filters.
        Filters:
        An optional dictionary of structured search constraints.
        Supported keys: category, brand, name, color, max_price.

        Apply filters only when the customer explicitly specifies
        these constraints. Use only supported keys and omit any
        filters that are not requested.

        max_price represents the maximum price in MAD.
        Use an empty dictionary {} when no filters are needed.

        Example:
        {"category": "Men / T-Shirts", "color": "White",
        "max_price": 300, "brand": "Casa Essentials",
        "size": "M"}
    
        """
        if filters is None:
            filters = {}
        
        if isinstance(filters, dict) and "filters" in filters and isinstance(filters["filters"], dict):
            filters = filters["filters"]
        results = await catalog_controller.hybrid_search(query=query, **filters)

        return [
            r.model_dump()
            for r in (results or [])
        ]
    
    return search_products