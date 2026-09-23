from stores.processing.ProcessingInterface import ProcessedDocument, ProcessingInterface


class ImageProcessor(ProcessingInterface):

    def load(self, file_path: str) -> list[ProcessedDocument]:
        try:
            from PIL import Image
            import pytesseract
        except ImportError:
            return [
                ProcessedDocument(
                    page_content=f"Image file: {file_path}. OCR dependencies are not installed.",
                    metadata={
                        "source": file_path,
                        "content_type": "image",
                        "ocr_status": "dependencies_missing",
                    },
                )
            ]

        image = Image.open(file_path)
        text = pytesseract.image_to_string(image).strip()

        if not text:
            text = f"Image file: {file_path}. No OCR text was detected."

        return [
            ProcessedDocument(
                page_content=text,
                metadata={
                    "source": file_path,
                    "content_type": "image_ocr",
                },
            )
        ]
