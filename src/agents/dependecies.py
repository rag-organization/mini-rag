from controllers import NLPController, CatalogController
from models.ProductModule import ProductModel
from dataclasses import dataclass

# async def create_agent_controllers(request):

#     nlp_controller = NLPController(
#             request.app.vector_db_client, 
#             request.app.embedding_client, 
#             request.app.generation_client,
#             request.app.template_parser
#             )
    
#     product_model = await ProductModel.create_instance(request.app.vector_db_client.db_client)
#     catalog_controller = CatalogController(
#         vectordb_client = request.app.vector_db_client, 
#         embedding_client = request.app.embedding_client, 
#         generation_client = request.app.generation_client,
#         product_model = product_model
#     )

#     return nlp_controller, catalog_controller
@dataclass(frozen=True)
class ToolsDependencies:
    nlp_controller: object
    catalog_controller: object
    project:object

    catalog_service: object
    outfit_service: object