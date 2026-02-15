from pathlib import Path
from typing import Annotated
from ollama import ChatResponse, Client
import typer

OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "reciprocity"

app = typer.Typer()


@app.command()
def run(
    path: Annotated[
        Path, typer.Argument(help="The path of the text file containing a recipe")
    ],
):
    recipe_raw = read_file(path)

    client = Client(host=OLLAMA_HOST)
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
    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)


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
