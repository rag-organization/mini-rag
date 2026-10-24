from langchain_core.tools import tool
## search knowledge base from rag



def create_product_search_tool(catalog_controller, query:str):

    @tool
    async def search_products():
        """
        Search the store's clothing catalog.
        Use this tool when a customer wants to discover
        products, such as shirts, jackets, trousers,
        or clothing suitable for an occasion.
        Supports semantic search, keyword search,
        and structured product filters.
        """
        results = await catalog_controller.hybrid_search(query)

        return [
            r.model_dumb()
            for r in (results or [])
        ]
    
    return search_products