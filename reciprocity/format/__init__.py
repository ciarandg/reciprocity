from rich.console import Console
from reciprocity.globals import OLLAMA_MODEL, OLLAMA_BASE, ollama_client
from rich.live import Live
from rich.text import Text
import sys
from importlib import resources
from pathlib import Path
from typing import Optional, TextIO

from rich import print

console_stderr = Console(stderr=True)


def format(
    input_file: Optional[Path] = None,
    output_file: Optional[Path] = None,
    print_thinking: bool = True,
):
    if not has_model(OLLAMA_MODEL):
        build_model()

    recipe_raw: str
    if not input_file:
        recipe_raw = sys.stdin.read()
    else:
        recipe_raw = _read_file(input_file)

    stream = ollama_client.chat(
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


def has_model(name: str) -> bool:
    models = ollama_client.list().models
    matches = [m for m in models if m["model"] == f"{name}:latest"]
    return len(matches) > 0


def build_model():
    if not has_model(OLLAMA_BASE):
        _pull_base_model()

    print(
        f"[yellow]Creating model {OLLAMA_MODEL} from base {OLLAMA_BASE}...[/yellow]",
        file=sys.stderr,
    )
    ollama_client.create(
        model=OLLAMA_MODEL,
        from_=OLLAMA_BASE,
        system=_system_prompt(),
    )
    print("[yellow]Success![/yellow]", file=sys.stderr)


def _pull_base_model():
    console_stderr.print(f"[yellow]Pulling base model {OLLAMA_BASE}...[/yellow]")

    stream = ollama_client.pull(OLLAMA_BASE, stream=True)

    text = Text("Pulling: 0%", style="yellow")
    with Live(text, console=console_stderr, refresh_per_second=10):
        for chunk in stream:
            if chunk.completed and chunk.total:
                pct = int(chunk.completed / chunk.total * 100)
                text.plain = f"Pulling: {pct}%"
    print("[yellow]Successfully pulled base model![/yellow]", file=sys.stderr)


def _read_file(path: Path) -> str:
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as _:
        print(f"Failed to read file: {path}")
        exit(1)


def _system_prompt() -> str:
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
