import json
import os
from typing import List, Optional, Dict
from pathlib import Path
import threading
from jobqueue_cli.models import Job, JobState

class JSONStorage:
    def __init__(self, storage_path: str = "jobqueue_data.json"):
        self.storage_path = Path(storage_path)
        self._lock = threading.Lock()
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Create storage file if it doesn't exist"""
        if not self.storage_path.exists():
            with self._lock:
                self.storage_path.write_text('{"jobs": {}, "config": {}}')
    
    def _load_data(self) -> Dict:
        with self._lock:
            try:
                return json.loads(self.storage_path.read_text())
            except (json.JSONDecodeError, FileNotFoundError):
                return {"jobs": {}, "config": {}}
    
    def _save_data(self, data: Dict):
        with self._lock:
            self.storage_path.write_text(json.dumps(data, indent=2))
    
    def save_job(self, job: Job):
        data = self._load_data()
        data["jobs"][job.id] = job.to_dict()
        self._save_data(data)
    
    def get_job(self, job_id: str) -> Optional[Job]:
        data = self._load_data()
        job_data = data["jobs"].get(job_id)
        return Job.from_dict(job_data) if job_data else None
    
    def get_jobs_by_state(self, state: JobState) -> List[Job]:
        data = self._load_data()
        jobs = []
        for job_data in data["jobs"].values():
            if job_data["state"] == state:
                jobs.append(Job.from_dict(job_data))
        return jobs
    
    def get_all_jobs(self) -> List[Job]:
        data = self._load_data()
        return [Job.from_dict(job_data) for job_data in data["jobs"].values()]
    
    def delete_job(self, job_id: str):
        data = self._load_data()
        if job_id in data["jobs"]:
            del data["jobs"][job_id]
            self._save_data(data)
    
    def save_config(self, config: Dict):
        data = self._load_data()
        data["config"] = config
        self._save_data(data)
    
    def load_config(self) -> Dict:
        data = self._load_data()
        return data.get("config", {})