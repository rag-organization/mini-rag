from contextlib import asynccontextmanager
from agents.agent import StylistAgent
from agents.dependecies import ToolsDependencies
from fastapi import FastAPI
from models.ProductModule import ProductModel
from models.ProjectModel import ProjectModel
from routes import base, data, nlp, product, agent, ragas
from helpers.config import get_config
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectoredb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.metrics import setup_metrics
from langchain_openai import ChatOpenAI
import os
from pathlib import Path
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from services import CatalogToolsService, OutfitService

from controllers import (
    CatalogController, 
    NLPController, 
    ProductRetrievalEvalController, 
    RetrievalEvalController, 
    ProjectController, 
    DataController, 
    ProcessController, 
    ProjectController, 
    BaseController
    )

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()

    print("application starting...")
    # app.mongodb_conn = AsyncMongoClient(config.MONGODB_URL) ## lazy connection,and it's load in the memory so no await needed
    # app.mongodb_client = app.mongodb_conn[config.MONGODB_DATABASE]
    postgres_conn = f"postgresql+asyncpg://{config.POSTGRES_USERNAME}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_MAIN_DATABASE}"
    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(app.db_engine, class_=AsyncSession, expire_on_commit=False)

    llm_provider_factory = LLMProviderFactory(setting=config)

    ## genration client
    app.generation_client = llm_provider_factory.create(provider = config.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = config.GENERATION_MODEL_ID)

    ## embedding client
    app.embedding_client = llm_provider_factory.create(provider = config.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id = config.EMBEDDING_MODEL_ID, embedding_size = config.EMBEDDING_MODEL_SIZE)

    ## vector db client
    vector_db_provider_factory = VectorDBProviderFactory(config, app.db_client)
    app.vector_db_client = vector_db_provider_factory.create(provider=config.VECTOR_DB_BACKEND)
    await app.vector_db_client.connect()

    #template
    app.template_parser = TemplateParser(language=config.PRIMARY_LANG, default_language=config.DEFAULT_LANG)

    #chatopenai for agent
    app.agent_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

    ## add checkpoint saver for short-term memory
    app.checkpointer = InMemorySaver()

    ## initialize the controllers
    app.project_id = config.FIXED_PROJECT_ID
    app.project_model = await ProjectModel.create_instance(app.db_client)
    app.product_model = await ProductModel.create_instance(app.db_client)
    app.project = await app.project_model.get_project_or_create_one(project_id=app.project_id)



    app.nlp_controller = NLPController(
        app.vector_db_client, 
        app.embedding_client, 
        app.generation_client, 
        app.template_parser
    )

    app.catalog_controller = CatalogController(
        vectordb_client = app.vector_db_client, 
        embedding_client = app.embedding_client, 
        generation_client = app.generation_client,
        product_model = app.product_model
    )
    app.retrieval_eval_controller = RetrievalEvalController(nlp_controller=app.nlp_controller)
    app.product_retrieval_eval_controller = ProductRetrievalEvalController(catalog_controller=app.catalog_controller)
    app.project_controller = ProjectController()

    ## agent services
    catalog_service = CatalogToolsService(db_client=app.db_client)
    outfit_service = OutfitService(db_client= app.db_client, catalog_controller=app.catalog_controller)

    ## 
    app.tools_dependencies = ToolsDependencies(
        nlp_controller = app.nlp_controller,
        catalog_controller = app.catalog_controller,
        project = app.project,
        catalog_service = catalog_service,
        outfit_service = outfit_service,
    )
    app.agent = StylistAgent(
        llm = app.agent_llm,
        dependencies=app.tools_dependencies,
        checkpointer=app.checkpointer
    )
    yield

    print("application shutting down...")
    # await app.mongodb_conn.close()
    await app.db_engine.dispose()
    app.vector_db_client.disconnect()


app = FastAPI(lifespan=lifespan)
# setup prometheus metrics
setup_metrics(app=app)

# uvicorn app:app --reload --ip 0.0.0.0 - ip forwarding to access the app from outside the container
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
app.include_router(ragas.ragas_router)
app.include_router(product.product_router)
app.include_router(agent.agent_router)