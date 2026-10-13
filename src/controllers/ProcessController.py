from typing import List

from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_text_splitters import RecursiveCharacterTextSplitter
from stores.processing import ProcessingProviderFactory
import os

class ProcessController(BaseController):
    def __init__(self, project_id:str):
        super().__init__()
        self.project_id = project_id
        self.file_path = ProjectController().get_project_path(project_id)
        self.processing_provider_factory = ProcessingProviderFactory()

    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id:str):
        file_path = os.path.join(self.file_path, file_id)
        file_ext = self.get_file_extension(file_id)

        if not os.path.exists(file_path):
            return None

        return self.processing_provider_factory.create(file_ext)
    
    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id)
        if loader:
            file_path = os.path.join(self.file_path, file_id)
            return loader.load(file_path)
        
        return None
                

    def process_file_content(self, file_content:list,file_id: str, chunk_size: int, overlap_size: int):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size, 
            length_function=len)

        # print(f"file content: {file_content}")

        chunks = text_splitter.create_documents(
            texts=[doc.page_content for doc in file_content],
            metadatas=[
                {
                    **doc.metadata,
                    "file_id": file_id,
                }
                for doc in file_content
            ],
        )

        # print(f"\n\n\nchunks: {chunks}")
        return chunks

    def simple_text_processer(self, texts: List[str], metadata:dict, chunk_size:int, tag_spliter:str = "\n"):

        full_text = "\n".join(texts)

        lines = [doc.strip() for doc in full_text.split(tag_spliter) if len(doc.strip())>1]

        chnks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + tag_spliter

            if len(current_chunk) > chunk_size:
                chnks.append({"page_content": current_chunk, "metadata": metadata})
                current_chunk = ""

        if len(current_chunk) > 0:
            chnks.append({"page_content": current_chunk, "metadata": metadata})

        return chnks
