import os
import sys
import json
from mistralai import Mistral

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.prompts import ACTION_JSON_PROMPT


class ActionGenerator:
    """Generates structured JSON outputs for action requests (mock execution only)."""
    
    def __init__(self, api_key, model_name="mistral-small-2503"):
        """
        Initialize the action generator.
        
        Args:
            api_key: Mistral API key
            model_name: LLM model to use
        """
        self.client = Mistral(api_key=api_key)
        self.model_name = model_name
    
    def generate_action(self, query):
        """
        Generate structured JSON for an action request.
        
        Args:
            query: User action request string
            
        Returns:
            dict: Parsed JSON action object
        """
        # Format prompt
        prompt = ACTION_JSON_PROMPT.format(query=query)
        
        # Call LLM
        response = self.client.chat.complete(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0  # Deterministic output
        )
        
        # Extract JSON from response
        json_str = response.choices[0].message.content.strip()
        
        # Clean up response - extract JSON only
        # Remove markdown code blocks if present
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        try:
            action_json = json.loads(json_str)
            return action_json
        except json.JSONDecodeError as e:
            # Fallback: return error structure
            return {
                "action": "error",
                "error": f"Failed to parse JSON: {str(e)}",
                "raw_output": json_str
            }
