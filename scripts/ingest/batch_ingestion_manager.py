#!/usr/bin/env python3
"""
Batch Ingestion Manager
Handles large-scale document ingestion with progress tracking and resumability
"""

import os
import sys
import time
import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from advanced_document_processor import AdvancedDocumentProcessor, ProcessingStats

@dataclass
class BatchJob:
    """Represents a batch ingestion job"""
    job_id: str
    file_paths: List[str]
    collection_name: str
    status: str = "pending"  # pending, running, completed, failed, paused
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress: Dict[str, Any] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
        if self.progress is None:
            self.progress = {
                "total_files": len(self.file_paths),
                "processed_files": 0,
                "failed_files": 0,
                "total_chunks": 0,
                "current_file": None
            }
        if self.errors is None:
            self.errors = []

class BatchIngestionManager:
    """Manages batch document ingestion with progress tracking"""
    
    def __init__(self, 
                 chroma_path: str = "/Users/andrejsp/ai/chroma_db",
                 max_workers: int = None,
                 job_storage_path: str = "/Users/andrejsp/ai/batch_jobs"):
        self.chroma_path = chroma_path
        self.max_workers = max_workers or min(mp.cpu_count(), 8)
        self.job_storage_path = job_storage_path
        self.active_jobs: Dict[str, BatchJob] = {}
        self.completed_jobs: Dict[str, BatchJob] = {}
        
        # Create job storage directory
        os.makedirs(job_storage_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{job_storage_path}/batch_ingestion.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_batch_job(self, 
                        file_paths: List[str], 
                        collection_name: str,
                        job_id: str = None) -> BatchJob:
        """Create a new batch ingestion job"""
        if job_id is None:
            job_id = f"batch_{int(time.time())}"
        
        # Validate file paths
        valid_paths = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                valid_paths.append(file_path)
            else:
                self.logger.warning(f"File not found: {file_path}")
        
        if not valid_paths:
            raise ValueError("No valid file paths provided")
        
        job = BatchJob(
            job_id=job_id,
            file_paths=valid_paths,
            collection_name=collection_name
        )
        
        self.active_jobs[job_id] = job
        self._save_job(job)
        
        self.logger.info(f"Created batch job {job_id} with {len(valid_paths)} files")
        return job
    
    def start_batch_job(self, job_id: str) -> bool:
        """Start a batch job"""
        if job_id not in self.active_jobs:
            self.logger.error(f"Job {job_id} not found")
            return False
        
        job = self.active_jobs[job_id]
        if job.status != "pending":
            self.logger.error(f"Job {job_id} is not in pending status")
            return False
        
        job.status = "running"
        job.started_at = time.time()
        self._save_job(job)
        
        # Start processing in background
        asyncio.create_task(self._process_batch_job(job))
        
        self.logger.info(f"Started batch job {job_id}")
        return True
    
    async def _process_batch_job(self, job: BatchJob):
        """Process a batch job asynchronously"""
        try:
            processor = AdvancedDocumentProcessor(self.chroma_path)
            
            # Process files in batches to avoid memory issues
            batch_size = 10
            for i in range(0, len(job.file_paths), batch_size):
                batch_files = job.file_paths[i:i + batch_size]
                
                # Update progress
                job.progress["current_file"] = batch_files[0] if batch_files else None
                self._save_job(job)
                
                # Process batch
                for file_path in batch_files:
                    try:
                        stats = processor.process_document(file_path, job.collection_name)
                        
                        # Update job progress
                        job.progress["processed_files"] += stats.processed_documents
                        job.progress["failed_files"] += stats.failed_documents
                        job.progress["total_chunks"] += stats.total_chunks
                        
                        if stats.errors:
                            job.errors.extend(stats.errors)
                        
                        self.logger.info(f"Processed {file_path} - {stats.total_chunks} chunks")
                        
                    except Exception as e:
                        job.progress["failed_files"] += 1
                        job.errors.append(f"Error processing {file_path}: {str(e)}")
                        self.logger.error(f"Error processing {file_path}: {str(e)}")
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            # Mark job as completed
            job.status = "completed"
            job.completed_at = time.time()
            job.progress["current_file"] = None
            
            # Move to completed jobs
            self.completed_jobs[job_id] = job
            del self.active_jobs[job_id]
            
            self._save_job(job)
            self.logger.info(f"Completed batch job {job_id}")
            
        except Exception as e:
            job.status = "failed"
            job.errors.append(f"Batch processing error: {str(e)}")
            self._save_job(job)
            self.logger.error(f"Batch job {job_id} failed: {str(e)}")
    
    def pause_batch_job(self, job_id: str) -> bool:
        """Pause a running batch job"""
        if job_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[job_id]
        if job.status == "running":
            job.status = "paused"
            self._save_job(job)
            self.logger.info(f"Paused batch job {job_id}")
            return True
        
        return False
    
    def resume_batch_job(self, job_id: str) -> bool:
        """Resume a paused batch job"""
        if job_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[job_id]
        if job.status == "paused":
            job.status = "running"
            self._save_job(job)
            # Restart processing
            asyncio.create_task(self._process_batch_job(job))
            self.logger.info(f"Resumed batch job {job_id}")
            return True
        
        return False
    
    def cancel_batch_job(self, job_id: str) -> bool:
        """Cancel a batch job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = "cancelled"
            self._save_job(job)
            del self.active_jobs[job_id]
            self.logger.info(f"Cancelled batch job {job_id}")
            return True
        
        return False
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a batch job"""
        job = self.active_jobs.get(job_id) or self.completed_jobs.get(job_id)
        if not job:
            return None
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "progress": job.progress,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "errors": job.errors
        }
    
    def list_jobs(self, status: str = None) -> List[Dict[str, Any]]:
        """List all jobs, optionally filtered by status"""
        all_jobs = {**self.active_jobs, **self.completed_jobs}
        
        if status:
            return [self.get_job_status(job_id) for job_id, job in all_jobs.items() 
                   if job.status == status]
        
        return [self.get_job_status(job_id) for job_id in all_jobs.keys()]
    
    def _save_job(self, job: BatchJob):
        """Save job state to disk"""
        job_file = os.path.join(self.job_storage_path, f"{job.job_id}.json")
        with open(job_file, 'w') as f:
            json.dump(asdict(job), f, indent=2)
    
    def load_jobs(self):
        """Load jobs from disk on startup"""
        for job_file in os.listdir(self.job_storage_path):
            if job_file.endswith('.json'):
                try:
                    with open(os.path.join(self.job_storage_path, job_file), 'r') as f:
                        job_data = json.load(f)
                        job = BatchJob(**job_data)
                        
                        if job.status in ["completed", "failed", "cancelled"]:
                            self.completed_jobs[job.job_id] = job
                        else:
                            self.active_jobs[job.job_id] = job
                            
                except Exception as e:
                    self.logger.error(f"Error loading job {job_file}: {str(e)}")

class BatchIngestionCLI:
    """Command-line interface for batch ingestion management"""
    
    def __init__(self):
        self.manager = BatchIngestionManager()
        self.manager.load_jobs()
    
    def create_job(self, file_paths: List[str], collection_name: str, job_id: str = None):
        """Create a new batch job"""
        try:
            job = self.manager.create_batch_job(file_paths, collection_name, job_id)
            print(f"✅ Created batch job: {job.job_id}")
            print(f"   Files: {len(job.file_paths)}")
            print(f"   Collection: {job.collection_name}")
            return job
        except Exception as e:
            print(f"❌ Error creating job: {e}")
            return None
    
    def start_job(self, job_id: str):
        """Start a batch job"""
        if self.manager.start_batch_job(job_id):
            print(f"✅ Started batch job: {job_id}")
        else:
            print(f"❌ Failed to start job: {job_id}")
    
    def list_jobs(self, status: str = None):
        """List all jobs"""
        jobs = self.manager.list_jobs(status)
        
        if not jobs:
            print("No jobs found")
            return
        
        print(f"\n📋 Batch Jobs ({len(jobs)} total)")
        print("=" * 50)
        
        for job in jobs:
            print(f"Job ID: {job['job_id']}")
            print(f"Status: {job['status']}")
            print(f"Progress: {job['progress']['processed_files']}/{job['progress']['total_files']} files")
            print(f"Chunks: {job['progress']['total_chunks']}")
            if job['errors']:
                print(f"Errors: {len(job['errors'])}")
            print("-" * 30)
    
    def monitor_job(self, job_id: str):
        """Monitor a specific job"""
        status = self.manager.get_job_status(job_id)
        if not status:
            print(f"❌ Job {job_id} not found")
            return
        
        print(f"\n🔍 Job Status: {job_id}")
        print("=" * 30)
        print(f"Status: {status['status']}")
        print(f"Progress: {status['progress']['processed_files']}/{status['progress']['total_files']} files")
        print(f"Chunks: {status['progress']['total_chunks']}")
        print(f"Current File: {status['progress']['current_file'] or 'None'}")
        
        if status['errors']:
            print(f"\n❌ Errors ({len(status['errors'])}):")
            for error in status['errors'][-5:]:  # Show last 5 errors
                print(f"   - {error}")

def main():
    """Main function for testing"""
    print("🚀 Batch Ingestion Manager Test")
    print("=" * 40)
    
    cli = BatchIngestionCLI()
    
    # Test with sample files
    sample_files = [
        "/Users/andrejsp/ai/sample_docs/python_guide.txt",
        "/Users/andrejsp/ai/sample_docs/machine_learning_basics.txt"
    ]
    
    # Create a test job
    job = cli.create_job(sample_files, "batch_test")
    if job:
        # Start the job
        cli.start_job(job.job_id)
        
        # Monitor the job
        time.sleep(2)
        cli.monitor_job(job.job_id)
        
        # List all jobs
        cli.list_jobs()

if __name__ == "__main__":
    main()