from typing import Optional, List
import logging
import logging.handlers
from datetime import datetime
import psutil
from .metrics import OperationMetrics

class DebugManager:
    """Main debug manager class for handling logging, metrics, and performance monitoring."""
    
    def __init__(self, config=None):
        self.debug_mode = False if config is None else config.debug_enabled
        self.metrics_history: List[OperationMetrics] = []
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging with file rotation and formatting."""
        logger = logging.getLogger('DataMasterPro')
        logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        
        # File handler with rotation
        handler = logging.handlers.RotatingFileHandler(
            'logs/app.log',
            maxBytes=1024*1024,  # 1MB
            backupCount=5
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        self.logger = logger
    
    def record_metrics(self, metrics: OperationMetrics):
        """Record operation metrics for analysis."""
        self.metrics_history.append(metrics)
        self.logger.debug(f"Operation recorded: {metrics}")
    
    def get_memory_usage(self):
        """Get current process memory usage."""
        return psutil.Process().memory_info().rss
    
    def clear_metrics(self):
        """Clear stored metrics history."""
        self.metrics_history.clear()
        self.logger.info("Metrics history cleared")
    
    def get_performance_summary(self):
        """Get summary of performance metrics."""
        if not self.metrics_history:
            return "No metrics recorded"
            
        total_ops = len(self.metrics_history)
        successful_ops = sum(1 for m in self.metrics_history if m.success)
        avg_duration = sum((m.end_time - m.start_time) for m in self.metrics_history) / total_ops
        
        return {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "failed_operations": total_ops - successful_ops,
            "average_duration": avg_duration,
            "current_memory": self.get_memory_usage()
        }