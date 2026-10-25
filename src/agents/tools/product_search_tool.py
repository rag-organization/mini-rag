from langchain_core.tools import tool
## search knowledge base from rag
from pydantic import BaseModel, Field
class ProductSearchInput(BaseModel):
    query: str = Field(
        description="Product name or natural-language shopping request"
    )


def create_product_search_tool(catalog_controller):

    @tool("search_product",
        args_schema=ProductSearchInput
        )
    async def search_products(query:str):
        """
        Search the store's clothing catalog.
        Use this tool when a customer wants to discover
        products, such as shirts, jackets, trousers,
        or clothing suitable for an occasion.
        Supports semantic search, keyword search,
        and structured product filters.
        """
        results = await catalog_controller.hybrid_search(query=query)

        return [
            r.model_dump()
            for r in (results or [])
        ]
    
    return search_products