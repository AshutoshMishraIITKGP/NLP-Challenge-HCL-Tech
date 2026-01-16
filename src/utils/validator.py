"""Input validation for security and safety."""
import re

class InputValidator:
    """Validates user input for security and safety."""
    
    MAX_LENGTH = 2000
    MIN_LENGTH = 1
    
    # Patterns to detect potential attacks
    SUSPICIOUS_PATTERNS = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
        r'\bexec\b',
        r'\beval\b',
        r'__import__',
        r'subprocess',
    ]
    
    @staticmethod
    def validate(query):
        """
        Validate user input.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check length
        if len(query) < InputValidator.MIN_LENGTH:
            return False, "Query is too short"
        
        if len(query) > InputValidator.MAX_LENGTH:
            return False, f"Query exceeds maximum length of {InputValidator.MAX_LENGTH} characters"
        
        # Check for suspicious patterns
        query_lower = query.lower()
        for pattern in InputValidator.SUSPICIOUS_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return False, "Query contains potentially unsafe content"
        
        # Check for excessive special characters (potential injection)
        special_char_ratio = sum(not c.isalnum() and not c.isspace() for c in query) / len(query)
        if special_char_ratio > 0.3:
            return False, "Query contains too many special characters"
        
        return True, None
