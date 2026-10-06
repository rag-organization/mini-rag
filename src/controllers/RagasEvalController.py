from helpers.config import get_config
setting = get_config()
from datasets import Dataset
from ragas import aevaluate
from ragas.metrics import (
    faithfulness,
    answer_correctness,
    context_recall,
    context_precision,
    answer_relevancy
)
from ragas.run_config import RunConfig
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_groq import ChatGroq

from langchain_core.rate_limiters import InMemoryRateLimiter

from helpers.config import Config
import json


class RagasEvalController:
    def __init__(self, setting:Config):
        self.config = setting
        self.llm_client =  self.get_llm_client(self.config.RAGAS_OPENAI_PROVIDER)
        self.embedding_client = self.get_embedding_client(setting.RAGAS_MISTRAL_PROVIDER)


    def get_llm_client(self,provider:str):
        provider = provider.lower()
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=0.5,  # Approximately one request every 2 seconds
            check_every_n_seconds=0.1,
            max_bucket_size=1,
        )
        if provider == "groq":
            model = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0,
            )
        
        elif provider == "mistral":
            model = ChatMistralAI(
                model="mistral-small-2603",
                api_key=self.config.MISTRAL_API_KEY,
                temperature=0,
                rate_limiter=rate_limiter
            )

        elif provider == "openai":
            model = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=self.config.OPENAI_API_KEY
            )

        else:
            raise ValueError(f"No llm provider configured for {provider}")

        return LangchainLLMWrapper(model)
    
    def get_embedding_client(self, provider:str):
        provider = provider.lower()

        if provider == "mistral":
            model = MistralAIEmbeddings(
                model="mistral-embed-2312",
                api_key=self.config.MISTRAL_API_KEY
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

        score = await aevaluate(
            dataset=dataset,
            llm=self.llm_client,
            embeddings=self.embedding_client,
            metrics=[
                faithfulness,
                answer_correctness,
                context_recall,
                context_precision,
                answer_relevancy
            ],
            batch_size=5,
            run_config=RunConfig(
            max_workers=1,
            timeout=300,
            max_retries=6,
            max_wait=60,
        )
        )

        return score

