#!/usr/bin/env python3
"""
git-gpt-search: a modular CLI for preparing, checking, and searching Git history embeddings,
with pluggable embedding models and LangChain integration for future LLM extensions.
"""

import json
import datetime
import subprocess
import typer
import shutil

from pathlib import Path
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate

from utilities.embeddings import _get_embeddings
from utilities.git_command_utilities import _extract_commits_with_message
from utilities.llm_provider import _get_llm_provider

app = typer.Typer()

root_dir = ".tmp"


# Utility to construct paths based on target folder
def _get_embeddings_store_paths(target_dir: Path) -> tuple[Path, Path]:
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
    node_name = target_dir.resolve().name.replace(" ", "_")
    embed_filename = f"{root_dir}/{node_name}-embeddings-{timestamp}.json"
    chroma_dir = Path(f"{root_dir}/.git_gpt_chroma_db_{timestamp}")
    return Path(embed_filename), chroma_dir


@app.command()
def prepare(
    folder: Path = typer.Argument(..., help="Path to the Git project folder"),
    provider: str = typer.Option("hf", "--provider", "-p", help="Embedding provider: hf or openai"),
    model: str = typer.Option(
        "BAAI/bge-small-en-v1.5", "--model", "-m",
        help="Embedding model: BAAI/bge-small-en-v1.5 or text-embedding-3-small",
    ),
):
    """
    Extract commits, generate embeddings, and index them in Chroma for future searches.
    """
    if not (folder / ".git").exists():
        typer.echo(
            "Error: provided folder is missing or is not a Git repository", err=True
        )
        raise typer.Exit(code=1)

    embed_file, chroma_dir = _get_embeddings_store_paths(folder)

    branch = subprocess.check_output(
        ["git", "-C", str(folder), "rev-parse", "--abbrev-ref", "HEAD"], text=True
    ).strip()
    typer.echo(f"Preparing embeddings for branch: {branch} at {folder}")

    docs = _extract_commits_with_message(folder)
    embeddings = _get_embeddings(provider, model)

    Chroma.from_documents(
        documents=docs, embedding=embeddings, persist_directory=str(chroma_dir)
    )

    payload = {
        "branch": branch,
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "provider": provider,
        "doc_count": len(docs),
        "path": str(folder),
        "chroma_dir": str(chroma_dir),
    }
    embed_file.write_text(json.dumps(payload, indent=2))
    typer.echo(f"✅ Embeddings indexed and stored in {embed_file}")


@app.command()
def list_embeddings():
    """
    List all available embeddings, newest first, with their metadata.
    """
    files = list(Path(root_dir).glob("*-embeddings-*.json"))
    if not files:
        typer.echo("No embeddings found in current directory.", err=True)
        raise typer.Exit(code=1)

    for file in sorted(files, reverse=True):
        try:
            data = json.loads(file.read_text())
            typer.echo(f"\nEmbeddings metadata from {file.name}:")
            typer.echo(f"  Branch      : {data['branch']}")
            typer.echo(f"  Created at  : {data['created_at']}")
            typer.echo(f"  Provider    : {data['provider']}")
            typer.echo(f"  Doc count   : {data['doc_count']}")
            typer.echo(f"  Chroma dir  : {data['chroma_dir']}")
        except Exception as e:
            typer.echo(f"\n⚠️  Failed to read {file.name}: {e}", err=True)


@app.command()
def search(
    query: str = typer.Argument(..., help="Query string (max 200 chars)"),
    provider: str = typer.Option(
        "hf", "--provider", "-p", help="Embedding provider: hf or openai"
    ),
    model: str = typer.Option(
        "BAAI/bge-small-en-v1.5", "--model", "-m",
        help="Embedding model: BAAI/bge-small-en-v1.5 or text-embedding-3-small",
    ),
    summarize: bool = typer.Option(
        False, "--summarize", "-s", help="Use LLM to summarize results"
    ),
    llm_provider: str = typer.Option(
        "openai", "--llm-provider", "-lp", help="LLM provider for summarization"
    ),
    llm_model: str = typer.Option(
        "gpt-4.1-nano", "--llm-model", "-lm", help="LLM model for summarization"
    ),
    k: int = typer.Option(5, "--limit", "-k", help="Max number of results to return"),
):
    """
    Search the latest embedding for a query and optionally summarize via LLM.
    """
    if len(query) > 200:
        typer.echo("Error: Query exceeds 200 characters.", err=True)
        raise typer.Exit(code=1)

    files = list(Path(root_dir).glob("*-embeddings-*.json"))
    if not files:
        typer.echo("No embeddings found. Run 'prepare' first.", err=True)
        raise typer.Exit(code=1)

    latest = sorted(files)[-1]
    data = json.loads(latest.read_text())
    chroma_dir = data["chroma_dir"]

    vectordb = Chroma(
        persist_directory=chroma_dir,
        embedding_function=_get_embeddings(provider, model),
    )
    docs = vectordb.similarity_search(query, k=k)
    commits = ""

    typer.echo(f"🔍 Top {len(docs)} matching commits:")
    for doc in docs:
        sha = doc.metadata.get("sha")
        author = doc.metadata.get("author")
        date = doc.metadata.get("date")
        message = doc.page_content[:100].splitlines()[0]
        typer.echo(f"- {sha}: {author} on {date}: {message}...")
        commits += f"-commit: {sha}: author: {author}, date: {date}, message: {message}...\n"

    if summarize:
        llm = _get_llm_provider(llm_provider, llm_model)

        system_prompt = """You are a helpful Engineer who understands how development works
        and answers questions about git commit changes. You are concise, accurate, and explain all commit messages
        which are relevant to the question clearly using developer-friendly language and provide all relevant details
        including the commit hash, author, date, and message. Answer only based on the commit messages provided.
        If you don't know the answer, say so."""

        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=system_prompt
            + "\n\nCommit Messages:\n{commits}\n\nQuestion:\n{question}",
        )

        chain = prompt_template | llm
        response = chain.invoke({"commits": commits, "question": query})

        # If the response is an object with `.content`
        if hasattr(response, "content"):
            answer = str(response.content)
        else:
            answer = str(response)  # fallback if LLM returns raw string

        typer.echo("\n🤖 LLM Answer:")
        typer.echo(answer.strip())


@app.command()
def cleanup():
    """
    Remove all embedding files and Chroma directories created by this script.
    """
    embed_files = list(Path(root_dir).glob("*-embeddings-*.json"))
    chroma_dirs = list(Path(root_dir).glob(".git_gpt_chroma_db_*"))

    for f in embed_files:
        f.unlink()
        typer.echo(f"🗑️ Deleted {f.name}")

    for d in chroma_dirs:
        shutil.rmtree(d, ignore_errors=True)
        typer.echo(f"🗑️ Deleted directory {d.name}")

    typer.echo("✅ Cleanup complete.")


if __name__ == "__main__":
    app()
