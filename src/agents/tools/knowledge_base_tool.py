
from langchain_core.tools import tool
from pydantic import BaseModel, Field
class KnowledgeBaseSearchInput(BaseModel):
    query: str = Field(
        description="Product name or natural-language shopping request"
    )

def create_knowledgebase_tool(nlp_controller, project):

    @tool("knowledgebase_search_tool",
          args_schema=KnowledgeBaseSearchInput)
    async def search_knowledge_base(query):
        """
                Search the store's knowledge base.
        
                Use this tool to find information from store
                documents, including return policies, shipping
                policies, clothing care instructions, and
                fashion guides.
        
                Do not use it to check live stock or prices.
        """
        results = await nlp_controller.hybrid_search(project=project, text=query)
        return [
            r.model_dump()
            for r in (results or [])
        ]

    return search_knowledge_base