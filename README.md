# Git Log Search

A developer utility that enables semantic search through Git commit history. This tool extracts commit history, generates vector embeddings, and allows you to search through your repository's history using natural language queries.

## Overview

This script scans your Git repository's commit history, extracts metadata (author, date, commit message), generates vector embeddings using configurable models (OpenAI or Hugging Face), and stores them in a Chroma vector database. You can then perform semantic searches to find relevant commits based on your queries.

**Current Features:**
- ✅ Git commit message search (implemented)
- 🔄 File diff search (planned)
- 🔄 Full commit content search (planned)

## Prerequisites

- Python 3.10 or higher
- pip

To install Python and pip, run:

```bash
#!/usr/bin/env bash
set -e

OS="$(uname)"
if [[ "$OS" == "Linux" ]]; then
  sudo apt-get update && sudo apt-get install -y python3 python3-pip
elif [[ "$OS" == "Darwin" ]]; then
  brew install python
else
  echo "Unsupported OS. Please install Python 3.10+ and pip manually: https://python.org"
  exit 1
fi

echo "Python version: $(python3 --version)"
echo "pip version: $(pip3 --version)"
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/git-log-search.git
cd git-log-search
```
2. Install dependencies (root folder):
```bash
pip install -r requirements.txt
```

## Quick Start

From the root folder, run:

```bash
# Get help
./message.py --help

# Prepare embeddings for a repository
./message.py prepare /path/to/your/repo

# Search for commits
./message.py search "When did we stop using sessions?"

# List embeddings that were created. Note that the system only uses the latest embeddings.
./message.py list-embeddings

# Clean up when done
./message.py cleanup
```

## 🚀 Recommended Usage

**We recommend using OpenAI models for the best search experience.** Here's the recommended workflow:

### 1. Set up your OpenAI API key
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Prepare embeddings with OpenAI
```bash
./message.py prepare /path/to/your/repo -p openai -m text-embedding-3-small
```

### 3. Search with AI-powered summarization
```bash
./message.py search "authentication changes" -p openai -m text-embedding-3-small -s -lp openai -lm gpt-4.1-nano
```

**Why OpenAI?** OpenAI's embedding models provide superior semantic understanding and the GPT models offer excellent summarization capabilities, making your search results more relevant and easier to understand.

## Commands

### `prepare` - Create Embeddings

Extracts commits from a Git repository, generates embeddings, and stores them in a vector database.

```bash
./message.py prepare <repository-path> [OPTIONS]
```

**Options:**
- `--provider` / `-p`: Embedding provider (`hf` or `openai`, default: `hf`)
- `--model` / `-m`: Embedding model name (default: `BAAI/bge-small-en-v1.5`)

**Examples:**
```bash
# Using default Hugging Face embeddings
./message.py prepare ./my-project

# Using OpenAI embeddings
./message.py prepare ./my-project -p openai -m text-embedding-3-small
```

### `search` - Search Commit History

Performs semantic search on the latest embeddings and returns relevant commits.

```bash
./message.py search <query> [OPTIONS]
```

**Options:**

**<u>Note</u>**: The provider and model should be the same as the ones used during preparation of embeddings

- `--provider` / `-p`: Embedding provider for search (`hf` or `openai`, default: `hf`)
- `--model` / `-m`: Embedding model for search (default: `BAAI/bge-small-en-v1.5`)
- `--summarize` / `-s`: Use LLM to summarize results (default: `False`)
- `--llm-provider` / `-lp`: LLM provider for summarization (default: `openai`)
- `--llm-model` / `-lm`: LLM model for summarization (default: `gpt-4.1-nano`)
- `--limit` / `-k`: Maximum number of results to return (default: `5`)

**Examples:**
```bash
# Basic search
./message.py search "When did we stop using sessions?"

# Search with LLM summarization
./message.py search "when were brand logos added" -s

# Search with specific embedding model
./message.py search "authentication changes" -p openai -m text-embedding-3-small

# Search with custom limit and summarization
./message.py search "database changes" -k 10 -s
```

### `list-embeddings` - View Available Embeddings

Lists all available embeddings with their metadata, sorted by creation date (newest first).

```bash
./message.py list-embeddings
```

**Output includes:**
- Branch name
- Creation timestamp
- Embedding provider and model
- Document count
- Chroma database directory

### `cleanup` - Remove All Data

Removes all embedding files and vector database directories created by this tool.

```bash
./message.py cleanup
```

## File Structure

The tool creates the following structure in a `.tmp` directory:

```
.tmp/
├── <repo-name>-embeddings-<timestamp>.json    # Embeddings metadata
└── .git_gpt_chroma_db_<timestamp>/            # Chroma vector database
```

## Supported Models

### Embedding Models
- **Hugging Face**: `BAAI/bge-small-en-v1.5` (default)
- **OpenAI**: `text-embedding-3-small`

### LLM Models (for summarization)
- **OpenAI**: `gpt-4.1-nano`, `gpt-4`, `gpt-3.5-turbo`

## Important Notes

1. **Model Consistency**: When searching, you must use the same embedding provider and model that was used during preparation.

2. **Query Length**: Search queries are limited to 200 characters.

3. **Repository Requirements**: The target directory must be a valid Git repository (contain a `.git` folder).

4. **Storage**: Embeddings and vector databases are stored locally and persist until explicitly cleaned up.

5. **Latest Search**: The search command always uses the most recent embeddings file.

## Limitations

1. **Model Interoperability**: Search queries must use the same embedding model that was used during preparation.

2. **File Management**: The tool doesn't automatically clean up old embeddings - use the `cleanup` command when needed.

3. **Current Scope**: Only commit message search is implemented; file diff and full content search are planned features.

## Environment Variables

**Required for OpenAI models:** You must set the following environment variable to use OpenAI embedding and LLM models:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Note:** This environment variable is mandatory when using `-p openai` or `-lp openai` options. The tool will fail if this is not set when attempting to use OpenAI services.

## Examples

### Workflow Example

```bash
# 1. Prepare embeddings for your project
./message.py prepare /Users/me/projects/my-app

# 2. Check what embeddings are available
./message.py list-embeddings

# 3. Search for specific changes
./message.py search "database migration changes"

# 4. Get an AI summary of the results
./message.py search "authentication system changes" -s

# 5. Clean up when done
./message.py cleanup
```

### Common Use Cases

- **Feature Tracking**: "When was the user authentication feature added?"
- **Bug Investigation**: "When did we fix the login bug?"
- **Refactoring History**: "When did we refactor the database layer?"
- **Dependency Updates**: "When did we update React to version 18?"

## Running the Example

Ensure **Prerequisites are met** before running the example.

To see a practical demonstration of how the tool works, you can run the example script provided in the repository. This script will run the typical workflow of the tool.

Run the example script with the following command from the `root` folder:

- Does not require any setup: `bash ./example/run-basic-example.sh`
- Requires OpenAI API key: `bash ./example/run-recommended-example.sh`
