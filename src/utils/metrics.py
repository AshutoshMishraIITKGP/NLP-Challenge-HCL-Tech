"""Performance monitoring and metrics collection."""
import time
import json
from datetime import datetime
from collections import defaultdict

class PerformanceMonitor:
    """Tracks system performance metrics."""
    
    def __init__(self):
        """Initialize metrics storage."""
        self.metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'info_queries': 0,
            'action_requests': 0,
            'response_times': [],
            'session_start': datetime.now().isoformat()
        }
        self.current_query_start = None
    
    def start_query(self):
        """Mark start of query processing."""
        self.current_query_start = time.time()
    
    def end_query(self, success=True, query_type=None):
        """Mark end of query processing and record metrics."""
        if self.current_query_start:
            response_time = time.time() - self.current_query_start
            self.metrics['response_times'].append(response_time)
            self.current_query_start = None
        
        self.metrics['total_queries'] += 1
        if success:
            self.metrics['successful_queries'] += 1
        else:
            self.metrics['failed_queries'] += 1
        
        if query_type == 'INFO_QUERY':
            self.metrics['info_queries'] += 1
        elif query_type == 'ACTION_REQUEST':
            self.metrics['action_requests'] += 1
    
    def get_summary(self):
        """Get performance summary."""
        avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times']) if self.metrics['response_times'] else 0
        success_rate = (self.metrics['successful_queries'] / self.metrics['total_queries'] * 100) if self.metrics['total_queries'] > 0 else 0
        
        return {
            'total_queries': self.metrics['total_queries'],
            'success_rate': f"{success_rate:.1f}%",
            'avg_response_time': f"{avg_response_time:.2f}s",
            'info_queries': self.metrics['info_queries'],
            'action_requests': self.metrics['action_requests']
        }
    
    def save_metrics(self, filepath='logs/metrics.json'):
        """Save metrics to file."""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump({
                **self.metrics,
                'summary': self.get_summary()
            }, f, indent=2)
