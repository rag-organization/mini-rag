from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProcessedDocument:
    page_content: str
    metadata: dict


class ProcessingInterface(ABC):

    @abstractmethod
    def load(self, file_path: str) -> list[ProcessedDocument]:
        pass
