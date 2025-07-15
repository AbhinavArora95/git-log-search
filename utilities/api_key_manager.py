import os
import typer

def _get_api_key(provider: str = "openai"):
    match provider:
        case "openai":
            return _get_api_key_openai()
        case _:
            typer.echo(f"Unknown embedding provider: {provider}", err=True)
            raise typer.Exit(code=1)

def _get_api_key_openai():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        typer.echo("Error: OPENAI_API_KEY is not set. Run export OPENAI_API_KEY='<key>'", err=True)
        raise typer.Exit(code=1)
    return key