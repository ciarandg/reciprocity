import sys
from pathlib import Path
from typing import Annotated

import typer
from ollama import Client
from rich import print

OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "reciprocity"

app = typer.Typer()


@app.command()
def run(
    path: Annotated[
        Path, typer.Argument(help="The path of the text file containing a recipe")
    ],
    print_thinking: Annotated[
        bool, typer.Option(help="Whether to stream model's thinking field to stderr")
    ] = True,
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
        message = chunk.get("message", {})
        thinking = message.get("thinking", None)
        content = message.get("content", None)

        if print_thinking and thinking:
            print(f"[blue]{thinking}[/blue]", end="", file=sys.stderr, flush=True)
        if content:
            print(content, end="", flush=True)


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
