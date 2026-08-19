# EasyRAG

EasyRAG is a lightweight, provider-agnostic **Retrieval-Augmented Generation (RAG)** chatbot. It ingests your Markdown knowledge base, stores it in a local Chroma vector database, and lets you chat with a Large Language Model that answers questions grounded in your documents.

The project is designed to be **plug-and-play**: pick your LLM and embedding provider in a `.env` file, drop your `.md` files into `docs/`, and start chatting — no code changes required.

## Features

- **Multi-provider LLM support** — Anthropic (Claude), OpenAI, Azure OpenAI, Google Vertex AI.
- **Multi-provider embeddings** — Local (HuggingFace / SentenceTransformers), OpenAI, Azure OpenAI, Voyage AI (via the `anthropic` option), Google Vertex AI.
- **Local vector store** — Uses [ChromaDB](https://www.trychroma.com/) persisted to disk (`./chroma_db`).
- **Markdown ingestion** — Recursively loads every `*.md` file from `./docs`, chunks it, and indexes it.
- **Configurable prompt & UI text** — Welcome message, default question, and system prompt are all defined in `.env`.
- **Dockerized** — Ready-to-use `Dockerfile` and `docker-compose.yml`, with helper scripts for Linux/macOS (`.sh`) and Windows (`.bat`).

## Project structure

```
EasyRAG/
├── app.py               # Interactive RAG chatbot entry point
├── factories.py         # Provider factories for LLMs and embeddings
├── init_db.py           # Builds the Chroma vector DB from ./docs
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container image definition
├── docker-compose.yml   # Compose service definition
├── build.sh / build.bat # Build the Docker image
├── init.sh  / init.bat  # (Re)build the vector database
├── start.sh / start.bat # Run the chatbot
├── .env.example         # Template for environment configuration
├── docs/                # Your Markdown knowledge base
└── chroma_db/           # Auto-generated persistent vector store
```

## Requirements

- **Docker** and **Docker Compose** (recommended path).
- *Or* Python 3.11+ with `pip` (for a local run without Docker).
- API keys for whichever cloud provider(s) you plan to use.

## Quick start (Docker)

### 1. Clone and configure

```bash
git clone <your-fork-url> EasyRAG
cd EasyRAG
cp .env.example .env
```

Edit `.env` and set at minimum:

- `LLM_PROVIDER` — one of `anthropic`, `openai`, `azure`, `vertex`.
- `EMBEDDINGS_PROVIDER` — one of `local`, `anthropic`, `openai`, `azure`, `vertex`.
- The API key(s) matching the providers you picked.
- The model name(s) — see [Provider reference](#provider-reference) below.

If you use **Vertex AI**, place your service-account JSON at `./gcp-key.json` — it is mounted into the container automatically.

### 2. Add your knowledge base

Drop any `*.md` files inside `docs/` directory (subdirectories are searched recursively):

```bash
cp /path/to/your/notes/*.md docs/
```

### 3. Build the image (⚠️WARNING: Building Docker Image is lengthy process)

Linux / macOS:

```bash
./build.sh
```

Windows:

```bat
build.bat
```

### 4. Build the vector database

This reads every Markdown file from `docs/`, splits it into 1000-character chunks (200-character overlap), embeds each chunk, and writes them into `./chroma_db`.

Linux / macOS:

```bash
./init.sh
```

Windows:

```bat
init.bat
```

Re-run this step any time you change the contents of `docs/`.

### 5. Start the chatbot

Linux / macOS:

```bash
./start.sh
```

Windows:

```bat
start.bat
```

You will see the welcome message and a `>` prompt. Type a question and press Enter; type `exit` to quit.

```
Welcome to the RAG Bot! (Type 'exit' to quit)

> What is EasyRAG?

Answer:
EasyRAG is a provider-agnostic RAG chatbot ...
```

## Running without Docker

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                 # edit as above
mkdir -p docs                        # add your .md files here

python init_db.py                    # build the vector DB
python app.py                        # start chatting
```

## Configuration reference

All configuration lives in `.env`. A full template is provided in `.env.example`.

### Core switches

| Variable              | Purpose                                              | Values |
|-----------------------|------------------------------------------------------|--------|
| `LLM_PROVIDER`        | Which chat model to load.                            | `anthropic`, `openai`, `azure`, `vertex` |
| `EMBEDDINGS_PROVIDER` | Which embedding model to use for indexing & retrieval. | `local`, `anthropic`, `openai`, `azure`, `vertex` |

### Provider reference

| Provider  | LLM variables                                                              | Embeddings variables                                                                 | Notes |
|-----------|----------------------------------------------------------------------------|---------------------------------------------------------------------------------------|-------|
| Local     | —                                                                          | `LOCAL_EMBEDDING_MODEL` (default `all-MiniLM-L6-v2`)                                   | Runs entirely on your machine via `sentence-transformers`. No API key needed. |
| Anthropic | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`                                     | `ANTHROPIC_EMBEDDING_MODEL` (a Voyage model id, e.g. `voyage-3`), `VOYAGE_API_KEY`     | Anthropic has no native embeddings API; the `anthropic` embeddings option routes through Voyage AI. |
| OpenAI    | `OPENAI_API_KEY`, `OPENAI_MODEL`                                           | `OPENAI_EMBEDDING_MODEL` (e.g. `text-embedding-3-small`)                              | |
| Azure     | `AZURE_AI_ENDPOINT`, `AZURE_AI_API_KEY`, `AZURE_API_VERSION`, `AZURE_MODEL`| Same connection variables + `AZURE_EMBEDDING_MODEL`                                   | `AZURE_MODEL` / `AZURE_EMBEDDING_MODEL` are **deployment names**, not model names. |
| Vertex    | `VERTEX_AI_PROJECT_ID`, `VERTEX_AI_LOCATION`, `VERTEX_MODEL`, `GOOGLE_APPLICATION_CREDENTIALS` | `VERTEX_EMBEDDING_MODEL`                                                              | Requires a service-account key at the path in `GOOGLE_APPLICATION_CREDENTIALS` (default `/app/gcp-key.json` in the container). |

### Application texts

| Variable            | Purpose |
|---------------------|---------|
| `WELCOME_MESSAGE`   | Greeting printed on startup. |
| `DEFAULT_QUESTION`  | Suggested question; also used as fallback when the user submits empty input. |
| `SYSTEM_PROMPT`     | System prompt for the LLM. Must contain `{context}` — if it doesn't, EasyRAG appends the context block automatically. |

## How it works

1. **Ingestion (`init_db.py`)** — Markdown files in `docs/` are loaded, split into ~1000-char chunks with 200-char overlap, embedded using the configured embedding model, and persisted into a local Chroma DB in `chroma_db/`.
2. **Retrieval (`app.py`)** — Each user question is embedded and used to retrieve the top-3 most similar chunks from Chroma.
3. **Generation** — The retrieved chunks are injected into the `{context}` placeholder of the system prompt and passed alongside the question to the configured LLM. The final grounded answer is printed to the terminal.

The chain is assembled with LangChain's `create_retrieval_chain` + `create_stuff_documents_chain`.

## Troubleshooting

- **`No documents found in ./docs`** — Ensure `docs/` exists at the project root and contains `*.md` files, then re-run `init.sh` / `init.bat`.
- **Provider errors on startup** — Verify that the API key and model name for the selected `LLM_PROVIDER` / `EMBEDDINGS_PROVIDER` are present in `.env`.
- **Changed the embedding provider or model** — Delete `chroma_db/` and re-run `init.sh` / `init.bat`; embeddings from different models are not interchangeable.
- **Vertex AI auth errors** — Confirm that `gcp-key.json` is present in the project root and that the service account has the required Vertex AI permissions.

