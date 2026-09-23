from enum import Enum

class ProcessingEnum(Enum):

    TXT = ".txt"
    PDF = ".pdf"
    CSV = ".csv"
    TSV = ".tsv"
    XLS = ".xls"
    XLSX = ".xlsx"
    PNG = ".png"
    JPG = ".jpg"
    JPEG = ".jpeg"
    WEBP = ".webp"
    BMP = ".bmp"
    TIFF = ".tiff"

    @classmethod
    def image_extensions(cls):
        return {
            cls.PNG.value,
            cls.JPG.value,
            cls.JPEG.value,
            cls.WEBP.value,
            cls.BMP.value,
            cls.TIFF.value,
        }

    @classmethod
    def table_extensions(cls):
        return {
            cls.CSV.value,
            cls.TSV.value,
            cls.XLS.value,
            cls.XLSX.value,
        }
