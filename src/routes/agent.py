from agents.dependecies import ToolsDependencies
from fastapi import APIRouter, Request
from controllers import CatalogController, NLPController
from models.ProductModule import ProductModel
from agents.agent import StylistAgent
from models.ProjectModel import ProjectModel
from .schemas.agent import ChatRequest
agent_router = APIRouter(
    prefix = "/api/v1/agent",
    tags = ["api_v1","agent"]
)

@agent_router.get("/")
def health():
    return {
        "message":"agent api"
    }
@agent_router.post("/chat/{project_id}")
async def chat(request:Request, project_id:int, chat_request:ChatRequest):

    
    nlp_controller = NLPController(
        request.app.vector_db_client, 
        request.app.embedding_client, 
        request.app.generation_client,
        request.app.template_parser
    )
    product_model = await ProductModel.create_instance(request.app.vector_db_client.db_client)
    catalog_controller = CatalogController(
        vectordb_client = request.app.vector_db_client, 
        embedding_client = request.app.embedding_client, 
        generation_client = request.app.generation_client,
        product_model = product_model
    )

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    
    dependencies = ToolsDependencies(nlp_controller=nlp_controller,catalog_controller=catalog_controller, project=project)
    agent = StylistAgent(llm=request.app.agent_llm,dependencies=dependencies, query=chat_request.message)
    response = await agent.chat(chat_request.message)

    return {
        "response":response
    }
