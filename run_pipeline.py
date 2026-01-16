#!/usr/bin/env python3
"""
RAG System Data Ingestion Pipeline Runner
Executes the complete pipeline: PDF -> Text -> Blocks -> Chunks
"""

import os
import sys
sys.path.append('src')

from ingestion.pdf_to_text import extract_text_from_pdf
from ingestion.block_extraction import process_raw_text
from ingestion.cdfg_chunker import process_blocks_to_chunks

def run_pipeline():
    """Execute the complete data ingestion pipeline"""
    
    # Step 1: PDF to Text
    print("Step 1: Extracting text from PDFs...")
    pdf_dir = "data/pdf"
    raw_text_dir = "data/raw_text"
    
    os.makedirs(raw_text_dir, exist_ok=True)
    
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            print(f"Processing {filename}...")
            extract_text_from_pdf(pdf_path, raw_text_dir)
    
    # Step 2: Block Extraction
    print("\nStep 2: Extracting structured blocks...")
    structured_blocks_dir = "data/structured_blocks"
    process_raw_text(raw_text_dir, structured_blocks_dir)
    
    # Step 3: CDFG Chunking
    print("\nStep 3: Creating CDFG chunks...")
    chunks_dir = "data/chunks"
    process_blocks_to_chunks(structured_blocks_dir, chunks_dir)
    
    print("\nPipeline completed successfully!")
    print(f"Final chunks saved in: {chunks_dir}")

if __name__ == "__main__":
    run_pipeline()