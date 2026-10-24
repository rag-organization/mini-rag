
from langchain_core.tools import tool

def create_knowledgebase_tool(nlp_controller, project, query:str):

    @tool
    async def search_knowledge_base():
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
            r.model_dumb()
            for r in (results or [])
        ]

    return search_knowledge_base