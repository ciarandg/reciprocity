from reciprocity.format import has_model, build_model
from reciprocity.globals import ollama_client, OLLAMA_HOST, OLLAMA_MODEL
import shutil
import sys

from rich import print


def setup():
    errors: list[str] = []

    is_ollama_working = True
    try:
        ollama_client.ps()
    except Exception:
        is_ollama_working = False
        errors.append(
            f"Broken configuration: could not connect to Ollama at {OLLAMA_HOST}"
        )

    if is_ollama_working and not has_model(OLLAMA_MODEL):
        build_model()

    if shutil.which("pdftoppm") is None:
        errors.append("Missing system dependency: pdftoppm (Poppler)")
    if shutil.which("tesseract") is None:
        errors.append("Missing system dependency: tesseract")

    if errors:
        print("[red]Dependency check failed:[/red]", file=sys.stderr)
        for err in errors:
            print(f"[red]- {err}[/red]", file=sys.stderr)
        exit(1)
    print("[green]All dependencies are correctly configured![/green]", file=sys.stderr)
