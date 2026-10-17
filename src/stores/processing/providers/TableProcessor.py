from stores.processing.ProcessingInterface import ProcessedDocument, ProcessingInterface
import csv
import os


class TableProcessor(ProcessingInterface):

    def load(self, file_path: str) -> list[ProcessedDocument]:
        ext = os.path.splitext(file_path)[-1].lower()

        if ext in [".csv", ".tsv"]:
            return self._load_delimited(file_path, "\t" if ext == ".tsv" else ",")

        return self._load_excel(file_path)

    def _load_delimited(self, file_path: str, delimiter: str) -> list[ProcessedDocument]:
        documents = []

        with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter=delimiter)
            for row_index, row in enumerate(reader, start=1):
                row_text = self._row_to_text(row)
                if not row_text:
                    continue

                documents.append(
                    ProcessedDocument(
                        page_content=row_text,
                        metadata={
                            "source": file_path,
                            "row": row_index,
                            "content_type": "table_row",
                        },
                    )
                )

        return documents

    def _load_excel(self, file_path: str) -> list[ProcessedDocument]:
        try:
            import pandas as pd
        except ImportError:
            return [
                ProcessedDocument(
                    page_content=f"Spreadsheet file: {file_path}. Excel dependencies are not installed.",
                    metadata={
                        "source": file_path,
                        "content_type": "spreadsheet",
                        "parser_status": "dependencies_missing",
                    },
                )
            ]

        documents = []
        sheets = pd.read_excel(file_path, sheet_name=None)

        for sheet_name, dataframe in sheets.items():
            dataframe = dataframe.fillna("")
            for row_index, row in dataframe.iterrows():
                row_text = self._row_to_text(row.to_dict())
                if not row_text:
                    continue

                documents.append(
                    ProcessedDocument(
                        page_content=row_text,
                        metadata={
                            "source": file_path,
                            "sheet": sheet_name,
                            "row": int(row_index) + 1,
                            "content_type": "spreadsheet_row",
                        },
                    )
                )

        return documents

    def _row_to_text(self, row: dict) -> str:
        parts = []
        for key, value in row.items():
            value = str(value).strip()
            if value:
                parts.append(f"{key}: {value}")

        return " | ".join(parts).strip()
