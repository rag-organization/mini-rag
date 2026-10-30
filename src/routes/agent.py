from uuid import uuid4

from agents.dependecies import ToolsDependencies
from dependencies import get_agent
from fastapi import APIRouter, Request, Depends
from controllers import CatalogController, NLPController
from models.ProductModule import ProductModel
from agents.agent import StylistAgent
from models.ProjectModel import ProjectModel
from .schemas.agent import ChatRequest
from services import CatalogToolsService, OutfitService

import json
from langchain_core.messages import ToolMessage

agent_router = APIRouter(
    prefix = "/api/v1/agent",
    tags = ["api_v1","agent"]
)

@agent_router.get("/")
def health():
    return {
        "message":"agent api"
    }


def extract_product_ids(agent_response: dict) -> list[int]:
    product_ids = []

    for message in agent_response["messages"]:
        if isinstance(message, ToolMessage) and message.name == "product_search_tool":
            products = json.loads(message.content)

            product_ids.extend(
                p["product_id"]
                for p in products
                if "product_id" in p
            )

    return list(dict.fromkeys(product_ids))

@agent_router.post("/chat/")
async def chat(
    chat_request:ChatRequest,
    agent: StylistAgent = Depends(get_agent),):

    ## calcule the request time
    import time
    start_time = time.time()

    
    conversation_id = str(chat_request.conversation_id or uuid4() )

    response = await agent.chat(chat_request.message, conversation_id)
    product_ids = extract_product_ids(response)
    #
    # calcule the request time
    end_time = time.time()
    request_time = end_time - start_time
    return {
        "response":response["messages"][-1].content,
        "products_ids":product_ids,
        "conversation_id":conversation_id,
        "request_time":request_time
    }

