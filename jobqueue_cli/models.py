import uuid
from datetime import datetime
from typing import Optional, Literal
from dataclasses import dataclass, asdict
import json

JobState = Literal["pending", "processing", "completed", "failed", "dead"]

@dataclass
class Job:
    id: str
    command: str
    state: JobState = "pending"
    attempts: int = 0
    max_retries: int = 3
    created_at: str = None
    updated_at: str = None
    last_error: Optional[str] = None
    next_retry_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    
    def should_retry(self) -> bool:
        return self.state == "failed" and self.attempts < self.max_retries
    
    def calculate_retry_delay(self, base_delay: int = 2) -> int:
        """Calculate exponential backoff delay in seconds"""
        return base_delay ** self.attempts