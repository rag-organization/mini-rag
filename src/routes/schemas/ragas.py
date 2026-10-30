from pydantic import BaseModel, Field


class RetrievalEvalSample(BaseModel):
    question: str = Field(min_length=1)
    relevant_chunk_ids: list[int] = Field(min_length=1)

class RetrievalEvalRequest(BaseModel):
    k: int = Field(default=5, ge=1)
    samples: list[RetrievalEvalSample] = Field(min_length=1)



class ProductRetrievalEvalSample(BaseModel):
    question: str = Field(min_length=1)
    relevant_chunk_ids: list[int] = Field(min_length=1)
    filters:dict
    query_type:str
    ground_truth_filters:dict
    relevant_count:int
    sample_id:str
    filter_count:int


class ProductRetrievalEvalRequest(BaseModel):
    k: int = Field(default=5, ge=1)
    samples: list[ProductRetrievalEvalSample] = Field(min_length=1)