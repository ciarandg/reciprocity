from ollama import ChatResponse, Client
import typer

OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "qwen3:1.7b"

app = typer.Typer()


@app.command()
def run(
    input: str,
    verbose: bool = False,
):
    if verbose:
        typer.echo("Verbose mode on")
    typer.echo(f"Processing {input}")
    client = Client(host=OLLAMA_HOST)
    response: ChatResponse = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Why is the sky blue? In 10 words",
            },
        ],
    )
    print(response.message.content)


def main():
    app()


if __name__ == "__main__":
    app()
