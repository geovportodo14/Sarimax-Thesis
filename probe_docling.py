from docling.document_converter import DocumentConverter
from pathlib import Path
import sys

def probe(pdf_path):
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    md = result.document.export_to_markdown()
    print(md)

if __name__ == "__main__":
    probe(sys.argv[1])
