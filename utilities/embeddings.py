import typer

from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.embeddings.base import Embeddings
from .api_key_manager import _get_api_key

def _get_embeddings(provider: str = "hf", model: str = "BAAI/bge-small-en-v1.5") -> Embeddings:
    if provider == "hf":
        return HuggingFaceEmbeddings(model_name=model)
    elif provider == "openai":
        _get_api_key()
        return OpenAIEmbeddings(model=model)
    else:
        typer.echo(f"Unknown embedding provider: {provider}", err=True)
        raise typer.Exit(code=1)