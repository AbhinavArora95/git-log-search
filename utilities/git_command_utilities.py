import subprocess
from pathlib import Path
from langchain.docstore.document import Document

# Extract hash, author, date, and commit message from git log at the target directory
def _extract_commits_with_message(target_dir: Path) -> list[Document]:
    raw = subprocess.check_output(
        ["git", "-C", str(target_dir), "log", "--pretty=format:%H%x1f%an%x1f%ad%x1f%s%x1e"],
        text=True
    )
    docs = []
    for entry in raw.strip().split("\x1e"):
        if not entry.strip():
            continue

        parts = entry.split("\x1f", 4)
        if len(parts) != 4:
            print(f"⚠️ Skipping malformed entry: {parts}")
            continue

        sha, author, date, message = parts
        metadata = {"sha": sha, "author": author, "date": date}
        docs.append(Document(page_content=message, metadata=metadata))
    return docs