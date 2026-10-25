from .knowledge_base_tool import create_knowledgebase_tool
from .product_search_tool import create_product_search_tool

class ToolFactory:

    def __init__(self, dependencies):
        self.dependencies = dependencies

    def create_tools(self):
        return [
            create_knowledgebase_tool(
                nlp_controller=self.dependencies.nlp_controller,
                project=self.dependencies.project,
            ),
            create_product_search_tool(
                catalog_controller=self.dependencies.catalog_controller,
            )
        ]
