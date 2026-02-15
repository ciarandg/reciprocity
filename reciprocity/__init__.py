import typer

app = typer.Typer()


@app.command()
def run(
    input: str,
    verbose: bool = False,
):
    if verbose:
        typer.echo("Verbose mode on")
    typer.echo(f"Processing {input}")


def main():
    app()


if __name__ == "__main__":
    app()
