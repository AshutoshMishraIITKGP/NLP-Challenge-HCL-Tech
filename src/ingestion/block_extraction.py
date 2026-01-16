import json
import os
import re

def extract_blocks(text_data):
    """Extract structured blocks from text with metadata"""
    blocks = []
    
    for page_data in text_data:
        page_num = page_data["page"]
        text = page_data["text"]
        
        # Split by paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        for i, paragraph in enumerate(paragraphs):
            # Detect block type
            block_type = "paragraph"
            if re.match(r'^[A-Z\s]+$', paragraph) and len(paragraph) < 100:
                block_type = "heading"
            elif re.search(r'\d+\.\d+|\d+%|Table|Figure', paragraph):
                block_type = "data"
            
            blocks.append({
                "id": f"page_{page_num}_block_{i}",
                "page": page_num,
                "type": block_type,
                "text": paragraph,
                "metadata": {
                    "word_count": len(paragraph.split()),
                    "char_count": len(paragraph)
                }
            })
    
    return blocks

def process_raw_text(input_dir, output_dir):
    """Process raw text files into structured blocks"""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_path = os.path.join(input_dir, filename)
            
            with open(input_path, 'r', encoding='utf-8') as f:
                text_data = json.load(f)
            
            blocks = extract_blocks(text_data)
            
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(blocks, f, indent=2, ensure_ascii=False)
            
            print(f"Processed {filename}: {len(blocks)} blocks extracted")

if __name__ == "__main__":
    input_dir = "data/raw_text"
    output_dir = "data/structured_blocks"
    
    process_raw_text(input_dir, output_dir)