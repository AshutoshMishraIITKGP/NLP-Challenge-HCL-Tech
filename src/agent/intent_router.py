import os
import sys
from mistralai import Mistral

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.prompts import INTENT_CLASSIFICATION_PROMPT


class IntentRouter:
    """Routes user queries to appropriate handlers based on intent classification."""
    
    def __init__(self, api_key, model_name="mistral-small-2503"):
        """
        Initialize the intent router.
        
        Args:
            api_key: Mistral API key
            model_name: LLM model to use
        """
        self.client = Mistral(api_key=api_key)
        self.model_name = model_name
    
    def classify_intent(self, query):
        """
        Classify user query into INFO_QUERY or ACTION_REQUEST.
        
        Args:
            query: User input string
            
        Returns:
            str: Either "INFO_QUERY" or "ACTION_REQUEST"
        """
        # Format prompt
        prompt = INTENT_CLASSIFICATION_PROMPT.format(query=query)
        
        # Call LLM
        response = self.client.chat.complete(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0  # Deterministic output
        )
        
        # Extract classification
        classification = response.choices[0].message.content.strip()
        
        # Clean up response - extract only the intent token
        if "INFO_QUERY" in classification:
            return "INFO_QUERY"
        elif "ACTION_REQUEST" in classification:
            return "ACTION_REQUEST"
        else:
            # Default to INFO_QUERY if uncertain
            return "INFO_QUERY"
