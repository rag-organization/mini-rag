import json
from pathlib import Path

from fastapi import APIRouter, Request
from models.ProjectModel import ProjectModel
from controllers.NLPControllers import NLPController
from controllers.RagasEvalController import RagasEvalController
import asyncio
import logging
from helpers.config import get_config
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

@ragas_router.get("/eval/evaluate")
async def evaluate():
    
    ragas_controller = RagasEvalController(setting=setting)

    reval_dataset_path = Path(__file__).parent.parent / "assets" / "eval" / "rag_results.json"
    # eval_dataset_path = "/asset/eval/eval_dataset.json"
    dataset = await ragas_controller.generate_ragas_dataset(reval_dataset_path)

    logger.info("start ragas evaluation...")
    score =  await ragas_controller.evaluate(dataset=dataset)
    logger.info("sevaluation ends successfully")
    
    # output_path = "assets/eval/ragas_report.csv"
    output_path = Path(__file__).parent.parent / "assets" / "eval" / "ragas_report.csv"

    score.to_pandas().to_csv(output_path, index=False, encoding="utf-8-sig")

    return {
        "message": "evaluation ends successfully",
        "score": score
    }
    

    