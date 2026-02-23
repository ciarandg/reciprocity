from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from rich import print


def read(input_files: list[Path]):
    for path in input_files:
        images: list[Image.Image]
        if path.suffix.lower() == ".pdf":
            images = convert_from_path(path, dpi=300)
        else:
            images = [Image.open(path)]
        ocr = [pytesseract.image_to_string(img) for img in images]
        for text in ocr:
            print(text)
