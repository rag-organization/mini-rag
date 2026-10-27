from .knowledge_base_tool import create_knowledgebase_tool
from .product_search_tool import create_product_search_tool
from .check_stock_tool import create_check_stock_tool
from .size_chart_tool import create_size_chart_tool
from .build_outfit_tool import create_outfit_tool
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
            ),
            create_check_stock_tool(
                catalog_service=self.dependencies.catalog_service,
            ),
            create_size_chart_tool(
                catalog_service=self.dependencies.catalog_service
            ),
            create_outfit_tool(
                outfit_service=self.dependencies.outfit_service
            )
        ]
