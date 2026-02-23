from reciprocity.read import read
from reciprocity.format import format_inner
import watchfiles
from os import mkdir
import logging
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


def watch(input_dir: Path, output_dir: Path):
    if not input_dir.exists():
        logger.info(
            "[red]Error: Input directory (`-i`/`--input-dir`) must already exist[/red]",
        )
        exit(1)
    if not input_dir.is_dir():
        logger.info(
            "[red]Error: Input directory (`-i`/`--input-dir`) must be a directory[/red]",
        )
        exit(1)
    if not output_dir.exists():
        logger.info(
            f"[yellow]Creating output directory {output_dir}...[/yellow]",
        )
        mkdir(output_dir)

    logger.info("[yellow]Starting daemon...[/yellow]")

    for changes in watchfiles.watch(input_dir):
        for op, path in changes:
            path = Path(path)

            match op:
                case watchfiles.Change.added:
                    logger.info(f"[yellow]Added: {path}[/yellow]")

                    ocr = read([path])
                    logger.info(
                        f"[yellow]Read {len(ocr.splitlines())} lines[/yellow]",
                    )
                    logger.debug(f"[blue]{ocr}[/blue]")

                    out_path = output_dir / (path.stem + ".md")

                    async def _run():
                        with open(out_path, "w", encoding="utf-8") as f:
                            async for chunk in format_inner(ocr):
                                f.write(chunk)
                                f.flush()

                    asyncio.run(_run())

                    logger.info(
                        f"[green]Wrote formatted output to {out_path}[/green]",
                    )

                case watchfiles.Change.modified:
                    logger.info(f"[yellow]Modified: {path}[/yellow]")

                case watchfiles.Change.deleted:
                    logger.info(f"[yellow]Deleted: {path}[/yellow]")
