import json
import os
import re

class SimpleTokenizer:
    def count_tokens(self, text):
        """Simple word-based token counting"""
        return len(text.split())

class CDFGChunker:
    def __init__(self, max_tokens=512, overlap_tokens=50):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.tokenizer = SimpleTokenizer()
    
    def count_tokens(self, text):
        """Count tokens in text"""
        return self.tokenizer.count_tokens(text)
    
    def chunk_blocks(self, blocks):
        """Chunk blocks using CDFG strategy"""
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for block in blocks:
            block_tokens = self.count_tokens(block["text"])
            
            # If single block exceeds max tokens, split it
            if block_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # Split large block
                chunks.extend(self._split_large_block(block))
                continue
            
            # If adding block exceeds limit, finalize current chunk
            if current_tokens + block_tokens > self.max_tokens and current_chunk:
                chunks.append(self._create_chunk(current_chunk))
                
                # Start new chunk with overlap
                overlap_blocks = self._get_overlap_blocks(current_chunk)
                current_chunk = overlap_blocks
                current_tokens = sum(self.count_tokens(b["text"]) for b in overlap_blocks)
            
            current_chunk.append(block)
            current_tokens += block_tokens
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk))
        
        return chunks
    
    def _create_chunk(self, blocks):
        """Create chunk from blocks"""
        text = "\n\n".join(block["text"] for block in blocks)
        pages = list(set(block["page"] for block in blocks))
        
        return {
            "id": f"chunk_{len(blocks)}_{min(pages)}_{max(pages)}",
            "text": text,
            "token_count": self.count_tokens(text),
            "block_count": len(blocks),
            "pages": sorted(pages),
            "blocks": [block["id"] for block in blocks]
        }
    
    def _split_large_block(self, block):
        """Split block that exceeds max tokens"""
        text = block["text"]
        sentences = text.split('. ')
        chunks = []
        current_text = ""
        
        for sentence in sentences:
            test_text = current_text + sentence + ". "
            if self.count_tokens(test_text) > self.max_tokens and current_text:
                chunks.append({
                    "id": f"{block['id']}_split_{len(chunks)}",
                    "text": current_text.strip(),
                    "token_count": self.count_tokens(current_text),
                    "block_count": 1,
                    "pages": [block["page"]],
                    "blocks": [block["id"]]
                })
                current_text = sentence + ". "
            else:
                current_text = test_text
        
        if current_text:
            chunks.append({
                "id": f"{block['id']}_split_{len(chunks)}",
                "text": current_text.strip(),
                "token_count": self.count_tokens(current_text),
                "block_count": 1,
                "pages": [block["page"]],
                "blocks": [block["id"]]
            })
        
        return chunks
    
    def _get_overlap_blocks(self, blocks):
        """Get blocks for overlap"""
        overlap_tokens = 0
        overlap_blocks = []
        
        for block in reversed(blocks):
            block_tokens = self.count_tokens(block["text"])
            if overlap_tokens + block_tokens <= self.overlap_tokens:
                overlap_blocks.insert(0, block)
                overlap_tokens += block_tokens
            else:
                break
        
        return overlap_blocks

def process_blocks_to_chunks(input_dir, output_dir):
    """Process structured blocks into CDFG chunks"""
    os.makedirs(output_dir, exist_ok=True)
    chunker = CDFGChunker()
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_path = os.path.join(input_dir, filename)
            
            with open(input_path, 'r', encoding='utf-8') as f:
                blocks = json.load(f)
            
            chunks = chunker.chunk_blocks(blocks)
            
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
            
            total_tokens = sum(chunk["token_count"] for chunk in chunks)
            print(f"Processed {filename}: {len(chunks)} chunks, {total_tokens} total tokens")

if __name__ == "__main__":
    input_dir = "data/structured_blocks"
    output_dir = "data/chunks"
    
    process_blocks_to_chunks(input_dir, output_dir)