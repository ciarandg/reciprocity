from reciprocity.watch import watch
from reciprocity.logging_config import setup_logging, LogLevel
from reciprocity.setup import setup
from reciprocity.format import format
from reciprocity.read import read
from pathlib import Path
from typing import Annotated, Optional

import typer

app = typer.Typer()


@app.callback()
def cli_main(
    log_level: LogLevel = typer.Option(
        LogLevel.info,
        "--log-level",
        case_sensitive=False,
        help="Logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG)",
    ),
):
    setup_logging(level=log_level)


@app.command(
    "setup",
    help="Checks for required system dependencies and builds Ollama model if necessary",
)
def cli_setup():
    setup()


@app.command("read", help="Converts images or PDFs of a recipe to plaintext")
def cli_read(
    input_files: Annotated[
        list[Path],
        typer.Option(
            "-i",
            "--input-files",
            help="Path(s) to images or PDF files containing a recipe",
        ),
    ],
):
    print(read(input_files))


@app.command(
    "format", help="Restructures a plaintext recipe to fit a consistent template"
)
def cli_format(
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
):
    format(input_file, output_file)


@app.command(
    "watch",
    help="Watches a directory for new files, processes them, and outputs to another directory",
)
def cli_watch(
    input_dir: Annotated[
        Path, typer.Option("-i", "--input-dir", help="The directory to watch")
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "-o", "--output-dir", help="The directory to output processed files to"
        ),
    ],
):
    watch(input_dir, output_dir)
