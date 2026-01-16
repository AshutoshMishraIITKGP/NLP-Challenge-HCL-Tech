import os
import sys
from mistralai import Mistral

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.prompts import RAG_ANSWERING_PROMPT


class AnswerGenerator:
    """Generates answers to user queries using RAG with strict grounding and citations."""
    
    def __init__(self, api_key, retriever, model_name="mistral-small-2503"):
        """
        Initialize the answer generator.
        
        Args:
            api_key: Mistral API key
            retriever: Retrieval system instance (already implemented)
            model_name: LLM model to use
        """
        self.client = Mistral(api_key=api_key)
        self.retriever = retriever
        self.model_name = model_name
    
    def generate_answer(self, query, top_k=5):
        """
        Generate an answer to the user query using retrieved context.
        
        Args:
            query: User question string
            top_k: Number of chunks to retrieve
            
        Returns:
            str: Formatted answer with citations
        """
        # Step 1: Retrieve relevant chunks
        retrieved_chunks = self.retriever.retrieve(query, top_k=top_k)
        
        if not retrieved_chunks:
            return "Answer:\nThe requested information is not available in the provided document.\n\nCitations:\nNone"
        
        # Step 2: Assemble context from retrieved chunks
        context_parts = []
        page_numbers = set()
        
        for chunk in retrieved_chunks:
            context_parts.append(f"[Page {chunk['page']}]: {chunk['text']}")
            page_numbers.add(chunk['page'])
        
        context = "\n\n".join(context_parts)
        
        # Step 3: Format prompt
        prompt = RAG_ANSWERING_PROMPT.format(context=context, query=query)
        
        # Step 4: Call LLM
        response = self.client.chat.complete(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer = response.choices[0].message.content.strip()
        
        return answer
