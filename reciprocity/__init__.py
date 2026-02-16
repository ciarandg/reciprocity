from pdf2image import convert_from_path
import sys
from importlib import resources
from pathlib import Path
from typing import Annotated, Optional, TextIO

import pytesseract
import typer
from ollama import Client
from PIL import Image
from rich import print

OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "reciprocity"
OLLAMA_BASE = "qwen3:1.7b"

app = typer.Typer()
client = Client(host=OLLAMA_HOST)


@app.command(help="Creates the Ollama model used for formatting")
def build_model():
    print(
        f"[yellow]Creating model {OLLAMA_MODEL} from base {OLLAMA_BASE}...[/yellow]",
        file=sys.stderr,
    )
    client.create(
        model=OLLAMA_MODEL,
        from_=OLLAMA_BASE,
        system=system_prompt(),
    )
    print("[yellow]Success![/yellow]", file=sys.stderr)


@app.command(help="Converts images or PDFs of a recipe to plaintext")
def read(
    input_files: Annotated[
        list[Path],
        typer.Option(
            "-i",
            "--input-files",
            help="Path(s) to images or PDF files containing a recipe",
        ),
    ],
):
    for path in input_files:
        images: list[Image.Image]
        if path.suffix.lower() == ".pdf":
            images = convert_from_path(path, dpi=300)
        else:
            images = [Image.open(path)]
        ocr = [pytesseract.image_to_string(img) for img in images]
        for text in ocr:
            print(text)


@app.command(help="Restrucutres a plaintext recipe to fit a consistent template")
def format(
    input_file: Annotated[
        Optional[Path],
        typer.Option(
            "-i",
            "--input-file",
            help="Path to text file containing a recipe (otherwise reads from stdin)",
        ),
    ] = None,
    output_file: Annotated[
        Optional[Path],
        typer.Option(
            "-o",
            "--output-file",
            help="Path to file for formatted recipe (otherwise writes to stdout)",
        ),
    ] = None,
    print_thinking: Annotated[
        bool, typer.Option(help="Streams model's thinking field to stderr")
    ] = True,
):
    if not has_model():
        build_model()

    recipe_raw: str
    if not input_file:
        recipe_raw = sys.stdin.read()
    else:
        recipe_raw = read_file(input_file)

    stream = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": recipe_raw,
            },
        ],
        stream=True,
    )

    content_out: TextIO
    if output_file is not None:
        content_out = open(output_file, "w")
    else:
        content_out = sys.stdout

    for chunk in stream:
        message = chunk.get("message", {})
        thinking = message.get("thinking", None)
        content = message.get("content", None)

        if print_thinking and thinking:
            print(f"[blue]{thinking}[/blue]", end="", file=sys.stderr, flush=True)

        if content:
            print(content, end="", file=content_out, flush=True)


def system_prompt() -> str:
    template = (
        resources.files("reciprocity.data")
        .joinpath("template.txt")
        .read_text(encoding="utf-8")
    )
    instructions = (
        resources.files("reciprocity.data")
        .joinpath("instructions.txt")
        .read_text(encoding="utf-8")
    )
    return f"""
TEMPLATE (copy exactly, do not modify structure):
{template}
INSTRUCTIONS:
{instructions}
"""


def has_model() -> bool:
    models = client.list().models
    matches = [m for m in models if m["model"] == f"{OLLAMA_MODEL}:latest"]
    return len(matches) > 0


def read_file(path: Path) -> str:
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as _:
        print(f"Failed to read file: {path}")
        exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
