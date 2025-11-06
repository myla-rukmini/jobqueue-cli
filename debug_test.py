import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jobqueue_cli.core import QueueManager
from jobqueue_cli.storage import JSONStorage

def test_processing():
    print("=== DEBUG TEST STARTED ===")
    
    storage = JSONStorage()
    queue_manager = QueueManager(storage)
    
    # Get a pending job
    job = queue_manager.get_next_pending_job()
    if job:
        print(f"Found job: {job.id}")
        print(f"Command: {job.command}")
        print(f"Before - State: {job.state}, Attempts: {job.attempts}")
        
        # Execute the job
        result = queue_manager.execute_job(job)
        print(f"Execution result: {result}")
        print(f"After - State: {job.state}, Attempts: {job.attempts}")
    else:
        print("No pending jobs found")
    
    print("=== DEBUG TEST COMPLETED ===")

if __name__ == "__main__":
    test_processing()