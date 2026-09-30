from pydantic import BaseModel
from typing import Optional
from models.ProjectModel import ProjectModel

class EvalRequest(BaseModel):
    project = ProjectModel.create_instance()