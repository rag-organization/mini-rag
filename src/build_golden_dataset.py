from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import ConfigDict
from ragas.testset import TestsetGenerator

from helpers.config import get_config
from stores.llm.LLMProviderFactory import LLMProviderFactory


TEST_SIZE = 25
DOCUMENTS_PATH = Path("assets/files")
OUTPUT_PATH = Path("assets/golden_dataset/golden_dataset.csv")
SUPPORTED_EXTENSIONS = {".txt", ".md"}


def load_documents(path: Path) -> list[Document]:
    documents = []

    for file_path in path.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={"source": str(file_path)},
            )
        )

    return documents


class ProviderChatModel(BaseChatModel):
    client: object
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def _llm_type(self) -> str:
        return "mini_rag_llm_provider"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        prompt = "\n".join([message.content for message in messages if message.content])
        response = self.client.generate_text(prompt=prompt)

        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(content=response or "")
                )
            ]
        )


class ProviderEmbeddings(Embeddings):
    def __init__(self, client):
        self.client = client

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.client.embed_text(text=texts, document_type="search_document")

    def embed_query(self, text: str) -> list[float]:
        embeddings = self.client.embed_text(text=text, document_type="search_query")
        return embeddings[0] if embeddings else []


config = get_config()
llm_provider_factory = LLMProviderFactory(setting=config)

generator_llm = llm_provider_factory.create(provider=config.GENERATION_BACKEND)
generator_llm.set_generation_model(model_id=config.GENERATION_MODEL_ID)

embedding_client = llm_provider_factory.create(provider=config.EMBEDDING_BACKEND)
embedding_client.set_embedding_model(
    model_id=config.EMBEDDING_MODEL_ID,
    embedding_size=config.EMBEDDING_MODEL_SIZE,
)

documents = load_documents(DOCUMENTS_PATH)
if not documents:
    raise ValueError(f"No documents found in {DOCUMENTS_PATH}")

generator = TestsetGenerator.from_langchain(
    llm=ProviderChatModel(client=generator_llm),
    embedding_model=ProviderEmbeddings(client=embedding_client),
)

testset = generator.generate_with_langchain_docs(
    documents,
    testset_size=TEST_SIZE,
)

test_df = testset.to_pandas()
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
test_df.to_csv(OUTPUT_PATH, index=False)
print(f"Golden dataset saved to {OUTPUT_PATH}")

#===========================================================#
from llama_index import SimpleDirectoryReader
from ragas.testset import TestsetGenerator
from langchain_openai import ChatOpenAI
from ragas.embeddings import OpenAIEmbeddings

dir_path = "./prompt-engineering-papers"
reader = SimpleDirectoryReader(dir_path, num_files_limit=2)
documents = reader.load_data()


import openai

TEST_SIZE = 25

# generator with openai models
generator_llm = ChatOpenAI(model="gpt-4o-mini")
critic_llm = ChatOpenAI(model="gpt-4o")
openai_client = openai.OpenAI()
embeddings = OpenAIEmbeddings(client=openai_client)

generator = TestsetGenerator.from_langchain(generator_llm, critic_llm, embeddings)

# generate testset
testset = generator.generate_with_llamaindex_docs(documents, test_size=TEST_SIZE)
test_df = testset.to_pandas()
test_df.head()