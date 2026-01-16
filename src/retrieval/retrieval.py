"""
Simple retrieval module for the RAG system.
This assumes FAISS index and embeddings are already built.
"""
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


class Retriever:
    """Retrieves relevant document chunks using FAISS vector search."""
    
    def __init__(self, index_path, chunks_path, model_name="intfloat/e5-large-v2"):
        """
        Initialize retriever with FAISS index and document chunks.
        
        Args:
            index_path: Path to FAISS index file
            chunks_path: Path to JSON file containing document chunks
            model_name: Embedding model name
        """
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load document chunks
        with open(chunks_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        
        # Load embedding model with increased timeout
        import os
        os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '60'
        self.model = SentenceTransformer(model_name)
    
    def retrieve(self, query, top_k=5):
        """
        Retrieve top-k most relevant chunks for the query.
        
        Args:
            query: User query string
            top_k: Number of chunks to retrieve
            
        Returns:
            list: List of chunk dictionaries with 'text' and 'page' keys
        """
        # Embed query with e5 format
        query_text = f"query: {query}"
        query_embedding = self.model.encode([query_text], normalize_embeddings=True)
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Retrieve chunks and format them
        results = []
        for idx in indices[0]:
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                # Extract page numbers from the chunk
                pages = chunk.get('pages', [])
                page = pages[0] if pages else 'Unknown'
                
                results.append({
                    'text': chunk.get('text', ''),
                    'page': page
                })
        
        return results
