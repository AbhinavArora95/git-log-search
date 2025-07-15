import typer
from langchain_openai import ChatOpenAI
from .api_key_manager import _get_api_key

def _get_llm_provider(provider: str = "openai", model: str = "gpt-4.1-nano"):
    match provider:
        case "openai":
            return _get_llm_provider_openai(model)
        case _:
            typer.echo(f"Unknown LLM provider: {provider}", err=True)
            raise typer.Exit(code=1)

def _get_llm_provider_openai(model: str = "gpt-4.1-nano"):
    _get_api_key()
    return ChatOpenAI(model=model)