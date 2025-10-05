# ============================================================================
# VECTOR DATABASE SERVICE (knowledge_ingestion/vector_store.py)
# ============================================================================
import os
import pickle
import numpy as np
from typing import List, Dict, Any
import faiss
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self, dimension: int = 384, index_path: str = "vector_index.faiss"):
        self.dimension = dimension
        self.index_path = index_path
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize FAISS index
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            with open(f"{index_path}.metadata", "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata = []
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to vector store"""
        texts = [doc['content'] for doc in documents]
        embeddings = self.embedding_model.encode(texts)
        
        self.index.add(np.array(embeddings).astype('float32'))
        self.metadata.extend(documents)
        
        self.save()
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        query_embedding = self.embedding_model.encode([query])
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'), k
        )
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['score'] = float(distances[0][i])
                results.append(result)
        
        return results
    
    def save(self):
        """Save index to disk"""
        faiss.write_index(self.index, self.index_path)
        with open(f"{self.index_path}.metadata", "wb") as f:
            pickle.dump(self.metadata, f)
    
    def delete_by_id(self, doc_ids: List[str]):
        """Delete documents by ID (requires rebuilding index)"""
        self.metadata = [doc for doc in self.metadata if doc['id'] not in doc_ids]
        
        # Rebuild index
        if self.metadata:
            texts = [doc['content'] for doc in self.metadata]
            embeddings = self.embedding_model.encode(texts)
            
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(np.array(embeddings).astype('float32'))
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.save()