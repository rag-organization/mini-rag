from stores.processing.providers.PDFProcessor import PDFProcessor
from pathlib import Path

def main():
    file_path = Path(__file__).parent.parent / "assets" / "files" / "3" / "b4Hf3xmgqU3x_07_Scanned_Operational_Records.pdf"
    docs = PDFProcessor().load(file_path)
    with open("parsed_dump.txt", "w", encoding="utf-8") as f:
        for d in docs:
            f.write(f"\n===== {d.metadata} =====\n{d.page_content}\n")

if __name__ == "__main__":
    main()
