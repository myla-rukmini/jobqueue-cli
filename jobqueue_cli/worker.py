import time
import threading
from typing import List
from jobqueue_cli.core import QueueManager
from jobqueue_cli.storage import JSONStorage
from jobqueue_cli.models import Job

class Worker:
    def __init__(self, queue_manager: QueueManager, worker_id: str):
        self.queue_manager = queue_manager
        self.worker_id = worker_id
        self._running = False
        self._thread = None
        self.current_job = None
    
    def start(self):
        """Start the worker in a background thread"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the worker gracefully"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
    
    def _run(self):
        """Main worker loop"""
        while self._running:
            job = self.queue_manager.get_next_pending_job()
            
            if job:
                self.current_job = job
                self.queue_manager.execute_job(job)
                self.current_job = None
            else:
                # No jobs available, sleep a bit
                time.sleep(1)

class WorkerManager:
    def __init__(self, queue_manager: QueueManager):
        self.queue_manager = queue_manager
        self.workers: List[Worker] = []
        self._config = {"max_workers": 3}
        self._running = False
    
    def start_workers(self, count: int = 1):
        """Start multiple workers and keep them running"""
        # Stop existing workers
        self.stop_workers()
        
        # Start new workers
        for i in range(count):
            worker = Worker(self.queue_manager, f"worker-{i+1}")
            worker.start()
            self.workers.append(worker)
        
        self._running = True
        print(f"Started {count} worker(s)")
        
        # Keep the workers running
        self._keep_alive()
    
    def _keep_alive(self):
        """Keep the main thread alive while workers are running"""
        try:
            while self._running and any(worker._running for worker in self.workers):
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_workers()
    
    def stop_workers(self):
        """Stop all workers gracefully"""
        self._running = False
        for worker in self.workers:
            worker.stop()
        self.workers.clear()
        print("All workers stopped")
    
    def get_worker_status(self) -> dict:
        """Get status of all workers"""
        status = {
            "active_workers": len(self.workers),
            "workers": []
        }
        
        for worker in self.workers:
            status["workers"].append({
                "id": worker.worker_id,
                "current_job": worker.current_job.id if worker.current_job else None,
                "running": worker._running
            })
        
        return status