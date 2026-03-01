import logging
from importlib.metadata import version
from pathlib import Path
from typing import Annotated, Optional

import typer

from reciprocity.config import get_config, config_file, get_config_dict
from reciprocity.format import format
from reciprocity.logging_config import LogLevel, setup_logging
from reciprocity.read import read
from reciprocity.setup import setup
from reciprocity.watch import watch

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.callback(invoke_without_command=True)
def cli_main(
    ctx: typer.Context,
    version_opt: bool = typer.Option(
        False,
        "--version",
        help="Show the application version and exit",
        is_eager=True,
    ),
    log_level: Optional[LogLevel] = typer.Option(
        None,
        "--log-level",
        case_sensitive=False,
        help="Logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG)",
    ),
):
    if version_opt:
        typer.echo(version("reciprocity"))
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        if log_level is not None:
            raise typer.BadParameter(
                "Missing subcommand.",
                param_hint="--log-level",
            )
        typer.echo(ctx.get_help())
        raise typer.Exit()

    config_log_level = get_config().logging.level
    setup_logging(level=log_level or LogLevel[config_log_level])
    logger.debug(f"Config file: {config_file()}")
    logger.debug(f"Loaded config:\n{get_config_dict()}")


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
