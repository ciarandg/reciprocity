import time
import logging
from reciprocity.globals import OLLAMA_MODEL, OLLAMA_BASE, ollama_client
import sys
from importlib import resources
from pathlib import Path
from typing import Optional, TextIO

logger = logging.getLogger(__name__)


def format(
    input_file: Optional[Path] = None,
    output_file: Optional[Path] = None,
):
    if not has_model(OLLAMA_MODEL):
        build_model()

    if input_file is None:
        recipe_raw = sys.stdin.read()
    else:
        recipe_raw = _read_file(input_file)

    if output_file is not None:
        content_out: TextIO = open(output_file, "w", encoding="utf-8")
    else:
        content_out = sys.stdout

    stream = ollama_client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": recipe_raw}],
        stream=True,
    )

    # Buffer for thinking text
    thinking_buffer = ""

    for chunk in stream:
        message = chunk.get("message", {})
        thinking = message.get("thinking")
        content = message.get("content")

        # Buffer thinking until a newline
        if thinking:
            thinking_buffer += thinking
            while "\n" in thinking_buffer:
                line, thinking_buffer = thinking_buffer.split("\n", 1)
                line = line.strip()
                if line:
                    logger.debug(f"[blue]{line}[/blue]")

        # Write output to stdout
        if content:
            print(content, end="", file=content_out, flush=True)

    # Flush any remaining thinking text
    if thinking_buffer:
        logger.debug(thinking_buffer)

    if output_file is not None:
        content_out.close()


def has_model(name: str) -> bool:
    models = ollama_client.list().models
    matches = [m for m in models if m["model"] == f"{name}:latest"]
    return len(matches) > 0


def build_model():
    if not has_model(OLLAMA_BASE):
        _pull_base_model()

    logger.info(
        f"[yellow]Creating model {OLLAMA_MODEL} from base {OLLAMA_BASE}...[/yellow]",
    )
    ollama_client.create(
        model=OLLAMA_MODEL,
        from_=OLLAMA_BASE,
        system=_system_prompt(),
    )
    logger.info("[yellow]Success![/yellow]")


def _pull_base_model():
    logger.info(f"[yellow]Pulling base model {OLLAMA_BASE}...[/yellow]")

    stream = ollama_client.pull(OLLAMA_BASE, stream=True)

    last_log_time = 0
    min_interval_secs = 5

    for chunk in stream:
        if chunk.completed and chunk.total:
            pct = int(chunk.completed / chunk.total * 100)
            now = time.time()
            if now - last_log_time >= min_interval_secs:
                logger.info(f"[yellow]Pulling: {pct}%[/yellow]")
                last_log_time = now

    logger.info("[yellow]Successfully pulled base model![/yellow]")


def _read_file(path: Path) -> str:
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as _:
        logger.error(f"Failed to read file: {path}")
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
