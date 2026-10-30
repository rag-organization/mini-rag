import json
from pathlib import Path
from uuid import uuid4

from agents.agent import StylistAgent
from dependencies import get_nlp_controller,get_catalog_controller,get_agent
from fastapi import APIRouter, Request
from models.ProductModule import ProductModel
from models.ProjectModel import ProjectModel
from controllers import (
    NLPController, 
    RagasEvalController, 
    RetrievalEvalController, 
    CatalogController, 
    ProductRetrievalEvalController
)
from routes.schemas.agent import ChatRequest
from routes.schemas.ragas import RetrievalEvalRequest, ProductRetrievalEvalRequest
import logging
from helpers.config import get_config
from fastapi import Depends
setting = get_config()


logger = logging.getLogger("uvicorn.error")

ragas_router = APIRouter(
    prefix="/api/v1/ragas",
    tags=["api_v1", "ragas"],
)



@ragas_router.get("/")
async def root():
    return {"message": "ragas api"}


@ragas_router.get("/eval/rag_answers/{project_id}")
async def get_rag_answers(request:Request, project_id:int):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller = NLPController(
                request.app.vector_db_client, 
                request.app.embedding_client, 
                request.app.generation_client,
                request.app.template_parser
                )

    ## load evaluation questions
    eval_dataset_path = Path(__file__).parent.parent / "assets" / "eval" / "eval_dataset.json"

    with open(eval_dataset_path, "r") as file:
        eval_dataset = json.load(file)

    i = 0
    eval_results = []
    
    for item in eval_dataset:

        question = item["question"]
        ground_truth = item["ground_truth"]

        if not question:
            logger.warning("question not found")
        if not ground_truth:
            logger.warning("ground_truth not found")

        answer, _, _, contexts = await nlp_controller.answer_rag_question(project=project,query=question, limit=3)
        logger.info("start appending rag answers...")

        eval_results.append(
            {
                "question":question or "",
                "answer":answer or "",
                "contexts":contexts or "",
                "ground_truth": ground_truth or ""
            }
        )
        logger.info(f"[ok] question {i+1}: {question[:40]}")
        i+=1
        
        logger.info("rag answering end successfully")

    
    output_path = Path(__file__).parent.parent / "assets" / "eval" / "rag_results.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(eval_results,file, ensure_ascii=False, indent=2)

    return {
        "message":f"{len(eval_results)} saved successfully to {output_path}"
    } 

# @ragas_router.get("/eval/evaluate")
# async def evaluate():
    
#     ragas_controller = RagasEvalController(setting=setting)

#     reval_dataset_path = Path(__file__).parent.parent / "assets" / "eval" / "rag_results.json"
#     # eval_dataset_path = "/asset/eval/eval_dataset.json"
#     dataset = await ragas_controller.generate_ragas_dataset(reval_dataset_path)

#     logger.info("start ragas evaluation...")
#     score =  await ragas_controller.evaluate(dataset=dataset)
#     logger.info("sevaluation ends successfully")
    
#     # output_path = "assets/eval/ragas_report.csv"
#     output_path = Path(__file__).parent.parent / "assets" / "eval" / "ragas_report.csv"

#     score.to_pandas().to_csv(output_path, index=False, encoding="utf-8-sig")

#     return {
#         "message": "evaluation ends successfully",
#         "score": score
#     }
    


## evaluate retrieval
@ragas_router.post("/eval/evaluate_retrieval/{project_id}")
async def evaluate_retrieval(request: Request, project_id: int, eval_request: RetrievalEvalRequest):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller = NLPController(
        request.app.vector_db_client,
        request.app.embedding_client,
        request.app.generation_client,
        request.app.template_parser,
    )
    controller = RetrievalEvalController(nlp_controller=nlp_controller)
    return await controller.evaluate(
        project=project,
        samples=[sample.model_dump() for sample in eval_request.samples],
        k=eval_request.k,
    )

## evaluate product hybrid product search 
@ragas_router.post("/eval/evaluate_product_search_retrieval")
async def evaluate_retrieval(request: Request):

    product_model = await ProductModel.create_instance(request.app.vector_db_client.db_client)
    catalog_controller = CatalogController(
        vectordb_client = request.app.vector_db_client, 
        embedding_client = request.app.embedding_client, 
        generation_client = request.app.generation_client,
        product_model = product_model
    )

    controller = ProductRetrievalEvalController(catalog_controller=catalog_controller)
    DATASET_PATH = (
        Path(__file__).resolve().parents[1]
        / "assets"
        / "retrieval_eval"
        / "retrieval_golden_dataset.json"
    )
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    return await controller.evaluate(
        samples=eval_data["samples"],
        k=eval_data.get("k",5),
    )

from evaluation.agent_eval_metrics import build_metrics
from evaluation.dataset import dataset
from deepeval.evaluate import CacheConfig, DisplayConfig
from deepeval.test_case import LLMTestCase, SingleTurnParams, ToolCall, ToolCallParams
from deepeval import evaluate
from deepeval.evaluate import AsyncConfig
from collections import defaultdict
from fastapi.encoders import jsonable_encoder

def summarize_metrics(result):
    data = jsonable_encoder(result)

    metrics = defaultdict(
        lambda: {
            "scores": [],
            "passed": 0,
            "failed": 0,
            "threshold": None,
        }
    )

    for test_case in data["test_results"]:
        for metric in test_case.get("metrics_data") or []:

            if metric.get("score") is None or metric.get("error"):
                continue

            name = metric["name"]
            item = metrics[name]

            item["scores"].append(metric["score"])
            item["threshold"] = metric.get("threshold")

            if metric.get("success") is True:
                item["passed"] += 1

            elif metric.get("success") is False:
                item["failed"] += 1

    summary = {}

    for name, item in metrics.items():
        scores = item["scores"]
        evaluated = len(scores)
        graded = item["passed"] + item["failed"]

        summary[name] = {
            "mean_score": round(sum(scores) / evaluated, 4),
            "mean_percentage": round(
                100 * sum(scores) / evaluated, 2
            ),
            "threshold": item["threshold"],
            "total_test_cases": evaluated,
            "passed": item["passed"],
            "failed": item["failed"],
            "pass_rate": (
                round(100 * item["passed"] / graded, 2)
                if graded else None
            ),
        }

    return summary

@ragas_router.post("/eval/evaluate/evaluate_agent")
async def evaluate_agent(
    agent: StylistAgent = Depends(get_agent),
    ):

    # conversation_id = str(chat_request.conversation_id or uuid4() )

    trace_metrics, single_turn_metrics = build_metrics()
    cache_config = CacheConfig(use_cache=False, write_cache=False)
    display_config = DisplayConfig(inspect_after_run=False)


    test_cases = []

    for golden in dataset.evals_iterator(
        metrics = trace_metrics,
        cache_config =  cache_config,
        display_config = display_config
    ):
        conversation_id = f"eval-{uuid4().hex}"
        result = await agent.chat(golden.input, conversation_id)
        response = result["messages"][-1].content

        tools_called = []

        for msg in result["messages"]:
            for tool_call in getattr(msg, "tool_calls", []) or []:
                tools_called.append(
                    ToolCall(
                        name = tool_call["name"],
                        input_parameters = tool_call["args"]
                    )
                )

        test_cases.append(
            LLMTestCase(
                input= golden.input,
                actual_output=response,
                expected_output=golden.expected_output,
                tools_called=tools_called,
                expected_tools=golden.expected_tools,
                    
            )
        )

    result = evaluate(
        test_cases=test_cases,
        metrics=single_turn_metrics,
        cache_config=cache_config,
        display_config=display_config,
        async_config=AsyncConfig(
        run_async=False
    )
    )

    summary = summarize_metrics(result)

    return {
        "message": "evaluation ends successfully",
        "summary": summary,
        "result": result
    }
