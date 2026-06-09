from __future__ import annotations

import chromadb
from pathlib import Path
from typing import Any

from rag.parser import parse_policy_markdown


class ChromaPolicyStore:
    """Student scaffold for the real Chroma-backed policy index."""

    def __init__(
        self,
        persist_directory: Path,
        embedding_model: Any,
        collection_name: str = "policy_chunks",
    ) -> None:
        self.embedding_model = embedding_model
        # Create persistent client
        self.client = chromadb.PersistentClient(path=str(persist_directory))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def ensure_index(self, markdown_path: Path) -> None:
        count = self.collection.count()
        if count == 0:
            print("Chroma collection is empty. Rebuilding index...")
            self.rebuild(markdown_path)
        else:
            print(f"Chroma collection loaded with {count} documents.")

    def rebuild(self, markdown_path: Path) -> None:
        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        chunks = parse_policy_markdown(markdown_text)
        if not chunks:
            print("No chunks found in the markdown policy.")
            return

        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk["rendered_text"])
            metadatas.append({
                "section_h2": chunk["section_h2"],
                "section_h3": chunk["section_h3"],
                "citation": chunk["citation"]
            })
            ids.append(f"chunk_{i}")

        embeddings = self.embedding_model.embed_documents(documents)

        try:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            print(f"Successfully rebuilt Chroma index with {len(chunks)} chunks.")
        except Exception as e:
            print(f"Error rebuilding index: {e}")

    def search(self, query: str, top_k: int = 4) -> list[dict[str, Any]]:
        query_embedding = self.embedding_model.embed_query(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        hits = []
        if results and results.get("documents"):
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0] if results.get("distances") else [0]*len(docs)
            
            for doc, meta, dist in zip(docs, metas, distances):
                hits.append({
                    "citation": meta.get("citation", "Unknown Section"),
                    "content": doc,
                    "distance": dist
                })
                
        return hits
