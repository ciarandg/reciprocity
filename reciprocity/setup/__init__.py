import logging
from reciprocity.format import has_model, build_model
from reciprocity.globals import ollama_client, OLLAMA_HOST, OLLAMA_MODEL
import shutil

logger = logging.getLogger(__name__)


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
        logger.error("[red]Dependency check failed:[/red]")
        for err in errors:
            logger.error(f"[red]- {err}[/red]")
        exit(1)
    logger.info("[green]All dependencies are correctly configured![/green]")
