"""Semantic Memory Store - Vector store for facts, domain knowledge, structured data."""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import chromadb
from langchain_openai import OpenAIEmbeddings


class SemanticMemoryStore:
    """Vector store for facts, domain knowledge, structured data."""
    
    def __init__(self, embeddings: OpenAIEmbeddings, collection_name: str = "semantic", persist_dir: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embeddings = embeddings
    
    def put(self, namespace: str, key: str, content: str, metadata: Dict[str, Any] = None):
        """Store or update a semantic memory."""
        doc_id = f"{namespace}:{key}"
        embedding = self.embeddings.embed_query(content)
        
        meta = metadata or {}
        meta.update({
            "namespace": namespace,
            "key": key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "semantic"
        })
        
        # Upsert (overwrites if exists)
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta]
        )
    
    def get(self, namespace: str, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific semantic memory."""
        doc_id = f"{namespace}:{key}"
        results = self.collection.get(ids=[doc_id])
        if results["ids"]:
            return {
                "content": results["documents"][0],
                "metadata": results["metadatas"][0]
            }
        return None
    
    def search(self, namespace: str, query: str, top_k: int = 5, filters: Dict = None) -> List[Dict[str, Any]]:
        """Semantic search with metadata filtering."""
        query_embedding = self.embeddings.embed_query(query)
        
        where = {"namespace": namespace}
        if filters:
            where.update(filters)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where if where else None
        )
        
        memories = []
        for i, doc_id in enumerate(results["ids"][0]):
            memories.append({
                "id": doc_id,
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None
            })
        
        return memories
    
    def delete(self, namespace: str, key: str):
        """Delete a semantic memory."""
        doc_id = f"{namespace}:{key}"
        self.collection.delete(ids=[doc_id])
    
    def clear_namespace(self, namespace: str):
        """Delete all memories in a namespace."""
        # Get all IDs in the namespace
        results = self.collection.get(where={"namespace": namespace})
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
    
    def clear_all(self):
        """Delete all semantic memories (clears entire collection)."""
        # Get all IDs
        results = self.collection.get()
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
    
    def delete_collection(self):
        """Delete the entire collection (nuclear option)."""
        self.client.delete_collection(name=self.collection.name)
        # Recreate empty collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )

