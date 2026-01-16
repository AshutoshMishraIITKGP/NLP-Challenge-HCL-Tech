import json
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_chunks(chunks_path):
    """Load chunks from JSON file"""
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    logger.info(f"Loaded {len(chunks)} chunks")
    return chunks

def generate_embeddings(chunks, model, batch_size=32):
    """Generate embeddings for chunks with batch processing"""
    texts = [f"passage: {chunk['text']}" for chunk in chunks]
    
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
        
        batch_embeddings = model.encode(batch, convert_to_numpy=True, normalize_embeddings=True)
        embeddings.extend(batch_embeddings.astype(np.float32))
    
    return np.array(embeddings)

def build_faiss_index(embeddings):
    """Build FAISS index for embeddings"""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    logger.info(f"Built FAISS index with {index.ntotal} vectors, dimension {dimension}")
    return index

def save_index_and_metadata(index, chunks, cache_dir):
    """Save FAISS index and metadata to cache"""
    os.makedirs(cache_dir, exist_ok=True)
    
    # Save FAISS index
    index_path = os.path.join(cache_dir, 'index.faiss')
    faiss.write_index(index, index_path)
    
    # Save metadata - adapt to actual chunk structure
    metadata = []
    for chunk in chunks:
        metadata.append({
            'chunk_id': chunk['id'],
            'section': chunk.get('section', 'Unknown'),
            'page_start': min(chunk['pages']) if chunk.get('pages') else 1,
            'page_end': max(chunk['pages']) if chunk.get('pages') else 1,
            'text': chunk['text']
        })
    
    metadata_path = os.path.join(cache_dir, 'metadata.pkl')
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    
    logger.info(f"Saved index and metadata to {cache_dir}")

def load_cached_index(cache_dir):
    """Load FAISS index and metadata from cache"""
    index_path = os.path.join(cache_dir, 'index.faiss')
    metadata_path = os.path.join(cache_dir, 'metadata.pkl')
    
    if os.path.exists(index_path) and os.path.exists(metadata_path):
        index = faiss.read_index(index_path)
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        logger.info(f"Loaded cached index with {index.ntotal} vectors")
        return index, metadata
    
    return None, None

def build_or_load_index():
    """Main function to build or load FAISS index"""
    chunks_path = 'data/chunks/Annual-Report-2024-25.json'
    cache_dir = 'data/faiss_cache'
    
    # Try to load from cache first
    index, metadata = load_cached_index(cache_dir)
    
    if index is not None and metadata is not None:
        logger.info("Using cached index")
        return index, metadata
    
    # Load chunks
    chunks = load_chunks(chunks_path)
    
    # Load embedding model
    logger.info("Loading embedding model: intfloat/e5-large-v2")
    model = SentenceTransformer('intfloat/e5-large-v2')
    
    # Generate embeddings
    logger.info("Generating embeddings...")
    embeddings = generate_embeddings(chunks, model)
    
    # Build FAISS index
    logger.info("Building FAISS index...")
    index = build_faiss_index(embeddings)
    
    # Save to cache
    save_index_and_metadata(index, chunks, cache_dir)
    
    return index, chunks

if __name__ == "__main__":
    index, metadata = build_or_load_index()
    logger.info("FAISS index ready for retrieval")