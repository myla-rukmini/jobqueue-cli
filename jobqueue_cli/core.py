import subprocess
import time
from datetime import datetime, timedelta
from typing import List, Optional
import threading
from jobqueue_cli.models import Job
from jobqueue_cli.storage import JSONStorage


class QueueManager:
    def __init__(self, storage: JSONStorage):
        self.storage = storage
        self._processing_lock = threading.Lock()
    
    def enqueue_job(self, command: str, job_id: Optional[str] = None, max_retries: int = 3) -> Job:
        job_id = job_id or f"job_{int(time.time())}_{hash(command) % 10000}"
        
        job = Job(
            id=job_id,
            command=command,
            max_retries=max_retries
        )
        
        self.storage.save_job(job)
        return job
    
    def get_next_pending_job(self) -> Optional[Job]:
        """Get next pending job, considering retry delays"""
        pending_jobs = self.storage.get_jobs_by_state("pending")
        failed_jobs = self.storage.get_jobs_by_state("failed")
        
        all_eligible = []
        
        # Add pending jobs
        all_eligible.extend(pending_jobs)
        
        # Add failed jobs that are ready for retry
        for job in failed_jobs:
            if job.should_retry():
                if job.next_retry_at is None:
                    all_eligible.append(job)
                else:
                    retry_time = datetime.fromisoformat(job.next_retry_at)
                    if datetime.utcnow() >= retry_time:
                        all_eligible.append(job)
        
        # Return the oldest job
        if all_eligible:
            return min(all_eligible, key=lambda j: j.created_at)
        
        return None
    
    def execute_job(self, job: Job) -> bool:
        """Execute a job command and return success status"""
        job.state = "processing"
        job.updated_at = datetime.utcnow().isoformat()
        self.storage.save_job(job)
        
        try:
            # Execute the command
            result = subprocess.run(
                job.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                job.state = "completed"
                job.last_error = None
            else:
                job.state = "failed"
                job.attempts += 1
                job.last_error = result.stderr or f"Exit code: {result.returncode}"
                
                # Set next retry time if applicable
                if job.should_retry():
                    delay = job.calculate_retry_delay()
                    next_retry = datetime.utcnow() + timedelta(seconds=delay)
                    job.next_retry_at = next_retry.isoformat()
                else:
                    job.state = "dead"
            
            job.updated_at = datetime.utcnow().isoformat()
            self.storage.save_job(job)
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            job.state = "failed"
            job.attempts += 1
            job.last_error = "Command timed out after 5 minutes"
            job.updated_at = datetime.utcnow().isoformat()
            
            if not job.should_retry():
                job.state = "dead"
            
            self.storage.save_job(job)
            return False
            
        except Exception as e:
            job.state = "failed"
            job.attempts += 1
            job.last_error = str(e)
            job.updated_at = datetime.utcnow().isoformat()
            
            if not job.should_retry():
                job.state = "dead"
            
            self.storage.save_job(job)
            return False
    
    def retry_dead_job(self, job_id: str) -> bool:
        """Move a dead job back to pending for retry"""
        job = self.storage.get_job(job_id)
        if not job or job.state != "dead":
            return False
        
        job.state = "pending"
        job.attempts = 0
        job.last_error = None
        job.next_retry_at = None
        job.updated_at = datetime.utcnow().isoformat()
        
        self.storage.save_job(job)
        return True
    
    def get_stats(self) -> dict:
        """Get queue statistics"""
        jobs = self.storage.get_all_jobs()
        stats = {
            "total": len(jobs),
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "dead": 0
        }
        
        for job in jobs:
            stats[job.state] += 1
        
        return stats