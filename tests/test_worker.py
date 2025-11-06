import time
from jobqueue_cli.core import QueueManager
from jobqueue_cli.storage import JSONStorage

def process_jobs():
    storage = JSONStorage()
    queue_manager = QueueManager(storage)
    
    print("Starting to process jobs...")
    processed = 0
    
    while True:
        job = queue_manager.get_next_pending_job()
        if job:
            print(f"Processing job: {job.id} - {job.command}")
            result = queue_manager.execute_job(job)
            print(f"Job {job.id} completed. State: {job.state}, Attempts: {job.attempts}")
            processed += 1
        else:
            print(f"No more jobs to process. Total processed: {processed}")
            break
        
        time.sleep(1)  # Small delay between jobs
    
    print("All jobs processed!")

if __name__ == "__main__":
    process_jobs()