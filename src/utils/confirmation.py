"""LLM-based confirmation classifier."""
from mistralai import Mistral

class ConfirmationClassifier:
    """Uses LLM to understand semantic meaning of confirmation responses."""
    
    def __init__(self, api_key):
        """Initialize with Mistral client."""
        self.client = Mistral(api_key=api_key)
    
    def classify_response(self, user_response, context):
        """
        Classify if user response is affirmative or negative.
        
        Args:
            user_response: User's response to confirmation question
            context: The action being confirmed
            
        Returns:
            str: "AFFIRMATIVE", "NEGATIVE", or "UNCLEAR"
        """
        prompt = f"""You are analyzing a user's response to a confirmation question.

Context: The system asked if the user wants to {context}

User's response: "{user_response}"

Classify the user's intent as EXACTLY one of:
- AFFIRMATIVE (user agrees/wants to proceed)
- NEGATIVE (user declines/wants to cancel)
- UNCLEAR (ambiguous, need clarification)

Examples:
"yes" → AFFIRMATIVE
"yeah, why not" → AFFIRMATIVE
"sure thing" → AFFIRMATIVE
"no thanks" → NEGATIVE
"not now" → NEGATIVE
"maybe later" → NEGATIVE
"what?" → UNCLEAR

Output ONLY one word (no explanation):"""

        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        result = response.choices[0].message.content.strip().upper()
        
        if "AFFIRMATIVE" in result:
            return "AFFIRMATIVE"
        elif "NEGATIVE" in result:
            return "NEGATIVE"
        else:
            return "UNCLEAR"
