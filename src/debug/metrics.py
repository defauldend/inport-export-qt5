from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class OperationMetrics:
    """Metrics for tracking operation performance and outcomes."""
    
    operation_name: str
    start_time: datetime
    end_time: datetime
    success: bool
    error_message: Optional[str] = None
    rows_affected: int = 0
    memory_before: int = 0
    memory_after: int = 0
    
    @property
    def duration(self) -> float:
        """Calculate operation duration in seconds."""
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def memory_delta(self) -> int:
        """Calculate memory change during operation."""
        return self.memory_after - self.memory_before
    
    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return (f"{self.operation_name} - {status} - "
                f"Duration: {self.duration:.3f}s - "
                f"Rows: {self.rows_affected}")
