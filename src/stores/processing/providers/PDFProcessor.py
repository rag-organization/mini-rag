from stores.processing.ProcessingInterface import ProcessedDocument, ProcessingInterface
import io


class PDFProcessor(ProcessingInterface):

    def load(self, file_path: str) -> list[ProcessedDocument]:
        try:
            import fitz
        except ImportError:
            return [
                ProcessedDocument(
                    page_content=f"PDF file: {file_path}. PyMuPDF is not installed.",
                    metadata={
                        "source": file_path,
                        "content_type": "pdf",
                        "parser_status": "dependencies_missing",
                    },
                )
            ]

        documents = []

        with fitz.open(file_path) as pdf:
            for page_index, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()
                if text:
                    documents.append(
                        ProcessedDocument(
                            page_content=text,
                            metadata={
                                "source": file_path,
                                "page": page_index,
                                "content_type": "pdf_text",
                            },
                        )
                    )

                documents.extend(self._extract_tables(page, file_path, page_index))
                documents.extend(self._extract_image_text(page, file_path, page_index))

        return documents

    def _extract_tables(self, page, file_path: str, page_index: int) -> list[ProcessedDocument]:
        documents = []

        if not hasattr(page, "find_tables"):
            return documents

        tables = page.find_tables()
        for table_index, table in enumerate(tables, start=1):
            rows = table.extract()
            table_text = self._rows_to_text(rows)
            if not table_text:
                continue

            documents.append(
                ProcessedDocument(
                    page_content=table_text,
                    metadata={
                        "source": file_path,
                        "page": page_index,
                        "table_index": table_index,
                        "content_type": "pdf_table",
                    },
                )
            )

        return documents

    def _extract_image_text(self, page, file_path: str, page_index: int) -> list[ProcessedDocument]:
        documents = []

        try:
            from PIL import Image
            import pytesseract
        except ImportError:
            return documents

        for image_index, image_info in enumerate(page.get_images(full=True), start=1):
            xref = image_info[0]
            import fitz
            pixmap = fitz.Pixmap(page.parent, xref)

            if pixmap.n >= 5:
                pixmap = fitz.Pixmap(fitz.csRGB, pixmap)

            image = Image.open(io.BytesIO(pixmap.tobytes("png")))
            image_text = pytesseract.image_to_string(image).strip()

            if not image_text:
                continue

            documents.append(
                ProcessedDocument(
                    page_content=image_text,
                    metadata={
                        "source": file_path,
                        "page": page_index,
                        "image_index": image_index,
                        "content_type": "pdf_image_ocr",
                    },
                )
            )

        return documents

    def _rows_to_text(self, rows: list[list[str]]) -> str:
        lines = []
        for row in rows:
            cells = [str(cell).strip() for cell in row if cell is not None and str(cell).strip()]
            if cells:
                lines.append(" | ".join(cells))

        return "\n".join(lines).strip()
