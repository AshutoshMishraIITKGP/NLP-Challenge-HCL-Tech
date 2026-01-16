"""Logging utility for tracking all system interactions."""
import logging
import os
from datetime import datetime

class SystemLogger:
    """Handles logging of all user interactions and system responses."""
    
    def __init__(self, log_dir="logs"):
        """Initialize logger with file and console handlers."""
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"system_{timestamp}.log")
        
        # Configure logger
        self.logger = logging.getLogger("AgenticRAG")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def log_query(self, query, intent=None):
        """Log user query."""
        self.logger.info(f"USER_QUERY | Intent: {intent} | Query: {query}")
    
    def log_response(self, response_type, content):
        """Log system response."""
        self.logger.info(f"SYSTEM_RESPONSE | Type: {response_type} | Content: {str(content)[:200]}")
    
    def log_error(self, error):
        """Log system error."""
        self.logger.error(f"ERROR | {str(error)}")
    
    def log_action(self, action_type, status):
        """Log action execution."""
        self.logger.info(f"ACTION | Type: {action_type} | Status: {status}")
