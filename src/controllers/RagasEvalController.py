from ..stores.llm.LLMProviderFactory import LLMProviderFactory
from helpers.config import get_config
setting = get_config()
from datasets import Dataset
from grok import chat
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_correctness,
    context_recall,
    context_precision,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_groq import ChatGroq
from helpers.config import Config
import json


class RagasEvalController:
    def __init__(self, setting:Config):
        self.llm_client =  self.get_llm_client(setting.RAGAS_MISTRAL_PROVIDER)
        self.embedding_client = self.get_embedding_client(setting.RAGAS_MISTRAL_PROVIDER)



    def get_llm_client(provider:str):
        provider = provider.lower()
        if provider == "groq":
            model = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0,
            )

        elif provider == "mistral":
            model = ChatMistralAI(
                model="mistral-small-latest",
                temperature=0,
            )

        elif provider == "openai":
            model = ChatOpenAI(
                model="gpt-4.1-mini",
                temperature=0,
            )

        else:
            raise ValueError(f"No llm provider configured for {provider}")

        return LangchainLLMWrapper(model)
    
    def get_embedding_client(provider:str):
        provider = provider.lower()

        if provider == "mistral":
            model = MistralAIEmbeddings(
                model="mistral-embed"
            )

        elif provider == "openai":
            model = OpenAIEmbeddings(
                model="text-embedding-3-small"
            )

        else:
            raise ValueError(
                f"No embedding provider configured for {provider}"
            )

        return LangchainEmbeddingsWrapper(model)

    async def generate_ragas_dataset(self, path:str):
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        dataset_dict = {
            "question": [d["question"] for d in data],
            "answer": [d["answer"] for d in data],
            "contexts": [d["contexts"] for d in data],
            "ground_truth":[ d["ground_truth"] for d in data],
        }
        return Dataset.from_dict(dataset_dict)

    async def evaluate(self, dataset):

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