"""Episodic Memory Store - Vector store for experiences, past interactions with recency bias."""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import chromadb
from langchain_openai import OpenAIEmbeddings


class EpisodicMemoryStore:
    """Vector store for experiences, past interactions with recency bias."""
    
    def __init__(self, embeddings: OpenAIEmbeddings, collection_name: str = "episodic", persist_dir: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embeddings = embeddings
    
    def put(self, namespace: str, key: str, content: str, metadata: Dict[str, Any] = None, salience_score: float = 1.0):
        """Store an episodic memory (only if salience_score > threshold)."""
        doc_id = f"{namespace}:{key}"
        embedding = self.embeddings.embed_query(content)
        
        meta = metadata or {}
        meta.update({
            "namespace": namespace,
            "key": key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "episodic",
            "salience": salience_score
        })
        
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta]
        )
    
    def search(self, namespace: str, query: str, top_k: int = 5, recency_weight: float = 0.3) -> List[Dict[str, Any]]:
        """Semantic search with recency bias."""
        query_embedding = self.embeddings.embed_query(query)
        
        # Get more results than needed for reranking
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,
            where={"namespace": namespace}
        )
        
        memories = []
        for i, doc_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i]
            timestamp_str = meta.get("timestamp", "")
            
            # Recency score (0-1, 1 = most recent)
            recency_score = 0.0
            if timestamp_str:
                try:
                    ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    age_days = (datetime.now(timezone.utc) - ts).total_seconds() / 86400
                    recency_score = 1.0 / (1.0 + age_days / 30)  # Decay over 30 days
                except:
                    pass
            
            # Combined score: similarity (1-distance) + recency
            similarity = 1.0 - results["distances"][0][i] if "distances" in results else 0.5
            combined_score = (1 - recency_weight) * similarity + recency_weight * recency_score
            
            memories.append({
                "id": doc_id,
                "content": results["documents"][0][i],
                "metadata": meta,
                "similarity": similarity,
                "recency_score": recency_score,
                "combined_score": combined_score
            })
        
        # Sort by combined score and return top_k
        memories.sort(key=lambda x: x["combined_score"], reverse=True)
        return memories[:top_k]
    
    def delete(self, namespace: str, key: str):
        """Delete an episodic memory."""
        doc_id = f"{namespace}:{key}"
        self.collection.delete(ids=[doc_id])
    
    def clear_namespace(self, namespace: str):
        """Delete all memories in a namespace."""
        # Get all IDs in the namespace
        results = self.collection.get(where={"namespace": namespace})
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
    
    def clear_all(self):
        """Delete all episodic memories (clears entire collection)."""
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

