from ..stores.llm.LLMProviderFactory import LLMProviderFactory
from helpers.config import get_config
setting = get_config()
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_correctness,
    context_recall,
    context_precision,
)
from .NLPControllers import NLPController

import json 


class RagasEvalController:
    def __init__(self):

        self.nlpcontroller = NLPController(
            vectordb_client=setting.VECTORDB_CLIENT,
            embedding_client=setting.EMBEDDING_BACKEND,
            generation_client=setting.GENERATION_BACKEND,
            # template_parser=setting.TEMPLATE_PARSER
        ) 
        self.llm_provider_factory = LLMProviderFactory(setting=setting)

        self.llm_client = self.llm_provider_factory.create(provider=setting.GENERATION_BACKEND)
        self.llm_client.set_generation_model(model_id=setting.GENERATION_MODEL_ID)

        self.embedding_client = self.llm_provider_factory.create(provider=setting.EMBEDDING_BACKEND)
        self.embedding_client.set_embedding_model(
            model_id=setting.EMBEDDING_MODEL_ID,
            embedding_size=setting.EMBEDDING_MODEL_SIZE,
        )


    def answer_rag_question(self, dataset):
        result = self.nlpcontroller.answer_rag_question(project=project, query=query, limit=limit)
    def generate_ragas_dataset(self, path:str):
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        dataset_dict = {
            "question": [d["question"] for d in data],
            "answer": [d["answer"] for d in data],
            "contexts": [d["contexts"] for d in data],
            "ground_truth":[ d["ground_truth"].values.tolist() for d in data],
        }
        return Dataset.from_dict(dataset_dict)

    def evaluate(self, dataset):
        score = evaluate(
            dataset=dataset,
            llm=self.llm_client,
            embedding=self.embedding_client,
            metrics=[
                faithfulness,
                answer_correctness,
                context_recall,
                context_precision
            ]
        )

        return score