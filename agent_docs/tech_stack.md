# Tech Stack
- **Language:** Python 3.11+
- **Package Manager:** `pip` (for Python environment management) and `volta` (for Node.js if applicable).
- **Environment:** Run `python3 -m venv .venv` and `source .venv/bin/activate` (or equivalent) to manage dependencies locally, then use `pip install -r src/requirements.txt`.
- **Orchestration:** LangGraph, LangChain Core
- **LLM:** Custom endpoint (`deepseek-v4-flash`) via `langchain-openai`
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`
- **Vector DB:** Chroma
