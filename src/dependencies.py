from fastapi import Depends, Request
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

from agents.agent import StylistAgent

async def get_nlp_controller(request: Request) -> NLPController:   
    """Dependency that yields the pre-initialized NLP Controller"""
    return request.app.nlp_controller


async def get_catalog_controller(request: Request) -> CatalogController:   
    """Dependency that yields the pre-initialized Catalog Controller"""
    return request.app.catalog_controller

async def get_project_controller(request: Request) -> ProjectController:   
    """Dependency that yields the pre-initialized Project Controller"""
    return request.app.project_controller

async def get_data_controller(request: Request) -> DataController:   
    """Dependency that yields the pre-initialized Data Controller"""
    return request.app.data_controller

async def get_process_controller(request: Request) -> ProcessController:   
    """Dependency that yields the pre-initialized Process Controller"""
    return request.app.process_controller

async def get_base_controller(request: Request) -> BaseController:   
    """Dependency that yields the pre-initialized Base Controller"""
    return request.app.base_controller

async def get_retrieval_eval_controller(request: Request) -> RetrievalEvalController:   
    """Dependency that yields the pre-initialized RetrievalEval Controller"""
    return request.app.retrieval_eval_controller

async def get_product_retrieval_eval_controller(request: Request) -> ProductRetrievalEvalController:
    """Dependency that yields the pre-initialized ProductRetrievalEval Controller"""
    return request.app.product_retrieval_eval_controller

async def get_agent(request: Request) -> StylistAgent:
    """Dependency that yields the pre-initialized StylistAgent"""
    return request.app.agent