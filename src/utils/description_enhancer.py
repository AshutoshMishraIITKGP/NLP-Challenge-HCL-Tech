"""Description enhancement for action requests."""
from mistralai import Mistral
import json
import os

class DescriptionEnhancer:
    """Enhances and refines action descriptions."""
    
    def __init__(self, api_key):
        """Initialize with Mistral client."""
        self.client = Mistral(api_key=api_key)
    
    def enhance_description(self, user_query, action_type):
        """Generate professional, polished description from user query using Mistral Large."""
        prompt = f"""You are a professional IT/HR ticket writer. Transform the user's informal query into a polished, professional ticket description.

User's query: "{user_query}"
Action type: {action_type}

Create a professional description that:
- Starts with "The user is experiencing..." or similar professional phrasing
- Captures the EXACT issue/request from the user (do not deviate from their primary concern)
- Uses technical, professional language
- Is clear and actionable for support staff
- 2-3 sentences maximum

Output ONLY the professional description:"""

        response = self.client.chat.complete(
            model="mistral-small-2503",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    
    def refine_description(self, user_input):
        """Transform user's custom description into professional format."""
        prompt = f"""Transform this user input into a professional IT/HR ticket description.

User input: "{user_input}"

Create a professional description that:
- Starts with "The user is experiencing..." or similar professional phrasing
- Captures the EXACT issue from the user (do not add or remove information)
- Fixes grammar and punctuation
- Uses professional, technical language
- Maintains the user's core message completely

Output ONLY the professional description:"""

        response = self.client.chat.complete(
            model="mistral-small-2503",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    
    def modify_action_json(self, current_json, user_modification_request):
        """Modify action JSON based on user's change request."""
        prompt = f"""You are modifying an action JSON based on user's request.

Current JSON:
{json.dumps(current_json, indent=2)}

User's modification request: "{user_modification_request}"

IMPORTANT INSTRUCTIONS:
1. Carefully read the user's request
2. Identify which field(s) need to be changed
3. Make the EXACT changes requested
4. If user mentions priority (high/medium/low/urgent), update the "priority" field
5. If user mentions date/time, add or update those fields
6. If user wants to expand/modify description, update the "description" field
7. Keep all other fields unchanged

Examples:
- "make priority high" → Change "priority" to "high"
- "change to urgent" → Change "priority" to "high"
- "add date 17th jan" → Add "date": "17th jan 2026"
- "expand the description" → Make description longer and more detailed

Output ONLY the complete modified JSON (no explanations, no text before or after):"""

        response = self.client.chat.complete(
            model="mistral-small-2503",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        try:
            result = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if result.startswith('```'):
                result = result.split('```')[1]
                if result.startswith('json'):
                    result = result[4:]
            return json.loads(result.strip())
        except Exception as e:
            print(f"\n[DEBUG] JSON parsing failed: {e}")
            print(f"[DEBUG] Raw response: {response.choices[0].message.content}")
            return current_json
    
    def check_satisfaction(self, user_response):
        """Check if user is satisfied with current ticket."""
        # First check if user is providing modifications
        if any(keyword in user_response.lower() for keyword in ['change', 'modify', 'update', 'add', 'set', 'make', 'expand', 'priority', 'date', 'time', 'description']):
            return False  # User wants to modify
        
        prompt = f"""The user is looking at a ticket and was asked "Do you want to modify the ticket?"

User response: "{user_response}"

Classify as:
- SATISFIED: User says "no", "don't modify", "looks good", "perfect", "done", "export it", "submit it", "that's all", "no more changes"
- UNSATISFIED: User says "yes" alone without any specific changes

IMPORTANT: 
- "no" means they DON'T want to modify = SATISFIED
- "yes" alone means they DO want to modify = UNSATISFIED
- If user provides specific changes, it's already handled before this

Respond with ONLY one word: SATISFIED or UNSATISFIED"""

        response = self.client.chat.complete(
            model="mistral-small-2503",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        result = response.choices[0].message.content.strip().upper()
        print(f"\n[DEBUG] Satisfaction check - User: '{user_response}' -> AI: {result}")
        return "SATISFIED" in result
    
    def wants_custom_description(self, user_response):
        """Check if user wants to write their own custom description."""
        prompt = f"""Does the user want to write their own custom description?

User response: "{user_response}"

Respond with ONLY one word: YES or NO"""

        response = self.client.chat.complete(
            model="mistral-small-2503",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        result = response.choices[0].message.content.strip().upper()
        return "YES" in result
    
    def is_description_modification(self, user_response):
        """Check if user is specifically trying to modify the description field."""
        prompt = f"""Analyze if the user wants to modify the DESCRIPTION field specifically.

User's response: "{user_response}"

Classify as:
- YES (user wants to modify/change/rewrite/expand the description text)
- NO (user wants to modify other fields like date, priority, issue_type, etc.)

Examples:
"make the description longer" → YES
"expand the description" → YES
"rewrite the description" → YES
"change the description to be more detailed" → YES
"add more info to description" → YES
"make it more detailed" → YES
"date is 17/01/25 time is 10pm" → NO
"change priority to high" → NO
"make it urgent" → NO
"update the meeting type" → NO

Output ONLY one word (YES or NO):"""

        response = self.client.chat.complete(
            model="mistral-small-2503",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        result = response.choices[0].message.content.strip().upper()
        return "YES" in result
