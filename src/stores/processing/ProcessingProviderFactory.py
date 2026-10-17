from models import ProcessingEnum
from .providers.TextProcessor import TextProcessor
from .providers.PDFProcessor import PDFProcessor
from .providers.ImageProcessor import ImageProcessor
from .providers.TableProcessor import TableProcessor


class ProcessingProviderFactory:

    def create(self, file_extension: str):
        ext = file_extension.lower()

        if ext == ProcessingEnum.TXT.value:
            return TextProcessor()

        if ext == ProcessingEnum.PDF.value:
            return PDFProcessor()

        if ext in ProcessingEnum.image_extensions():
            return ImageProcessor()

        if ext in ProcessingEnum.table_extensions():
            return TableProcessor()

        return None
