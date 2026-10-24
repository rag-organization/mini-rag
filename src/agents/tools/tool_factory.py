from .knowledge_base_tool import create_knowledgebase_tool
from .product_search_tool import create_product_search_tool

class ToolFactory:

    def __init__(self, dependencies, query:str):
        self.dependencies = dependencies
        self.query = query

    def create_tools(self):
        return [
            create_knowledgebase_tool(
                nlp_controller=self.dependencies.nlp_controller,
                project=self.dependencies.project,
                query= self.query
            ),
            create_product_search_tool(
                catalog_controller=self.dependencies.catalog_controller,
                query= self.query
            )
        ]
