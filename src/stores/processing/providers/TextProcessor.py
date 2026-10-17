from stores.processing.ProcessingInterface import ProcessedDocument, ProcessingInterface


class TextProcessor(ProcessingInterface):

    def load(self, file_path: str) -> list[ProcessedDocument]:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        return [
            ProcessedDocument(
                page_content=text,
                metadata={
                    "source": file_path,
                    "content_type": "text",
                },
            )
        ]
