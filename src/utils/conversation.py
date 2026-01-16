"""Conversation history management."""
from datetime import datetime
from collections import deque

class ConversationHistory:
    """Manages conversation history and context."""
    
    def __init__(self, max_history=10):
        """Initialize with maximum history size."""
        self.history = deque(maxlen=max_history)
    
    def add_exchange(self, query, response, intent):
        """Add a query-response exchange to history."""
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'intent': intent
        })
    
    def get_context(self, last_n=3):
        """Get last N exchanges as context string."""
        if not self.history:
            return ""
        
        recent = list(self.history)[-last_n:]
        context_parts = []
        
        for exchange in recent:
            context_parts.append(f"User: {exchange['query']}")
            if exchange['intent'] == 'INFO_QUERY':
                context_parts.append(f"Assistant: {exchange['response'][:200]}...")
            else:
                context_parts.append(f"Assistant: [Action: {exchange['response'].get('action', 'unknown')}]")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear conversation history."""
        self.history.clear()
