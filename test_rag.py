import sys
from pathlib import Path

# Add src to pythonpath so we can import app
sys.path.append(str(Path(__file__).parent / "src"))

from rag.embeddings import SentenceTransformerEmbeddings
from rag.vector_store import ChromaPolicyStore

def main():
    print("Loading embedding model...")
    embedding_model = SentenceTransformerEmbeddings("sentence-transformers/all-MiniLM-L6-v2")
    
    print("Initializing ChromaPolicyStore...")
    chroma_dir = Path("src/.chroma")
    policy_path = Path("data/policy_mock_vi.md")
    
    store = ChromaPolicyStore(
        persist_directory=chroma_dir,
        embedding_model=embedding_model
    )
    
    print(f"Ensuring index for {policy_path}...")
    store.ensure_index(policy_path)
    
    print("\n--- Test Search: 'trả hàng' ---")
    results = store.search("trả hàng", top_k=2)
    for i, r in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Citation: {r['citation']}")
        print(f"Distance: {r['distance']:.4f}")
        print(f"Content:\n{r['content']}")

if __name__ == "__main__":
    main()
