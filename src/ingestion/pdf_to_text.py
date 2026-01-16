import PyPDF2
import os
import json

def extract_text_from_pdf(pdf_path, output_dir):
    """Extract text from PDF with page markers"""
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    text_data = []
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            text_data.append({
                "page": page_num + 1,
                "text": text.strip()
            })
    
    output_path = os.path.join(output_dir, f"{filename}.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(text_data, f, indent=2, ensure_ascii=False)
    
    return output_path

if __name__ == "__main__":
    pdf_dir = "data/pdf"
    output_dir = "data/raw_text"
    
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            print(f"Processing {filename}...")
            extract_text_from_pdf(pdf_path, output_dir)
            print(f"Extracted text saved to {output_dir}")