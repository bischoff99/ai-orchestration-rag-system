#!/usr/bin/env python3
"""
Maximize Document Ingestion
Comprehensive system for maximizing document ingestion capabilities
Based on Context7 best practices and advanced techniques
"""

import os
import sys
import time
import asyncio
import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from advanced_document_processor import AdvancedDocumentProcessor, ProcessingStats
from batch_ingestion_manager import BatchIngestionManager, BatchJob
from ingestion_analytics import IngestionAnalytics, IngestionMonitor

class IngestionMaximizer:
    """Main class for maximizing document ingestion capabilities"""
    
    def __init__(self, 
                 chroma_path: str = "/Users/andrejsp/ai/chroma_db",
                 analytics_db_path: str = "/Users/andrejsp/ai/ingestion_analytics.db"):
        self.chroma_path = chroma_path
        self.processor = AdvancedDocumentProcessor(chroma_path)
        self.batch_manager = BatchIngestionManager(chroma_path)
        self.analytics = IngestionAnalytics(analytics_db_path)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/Users/andrejsp/ai/ingestion_maximizer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def discover_documents(self, 
                          root_path: str, 
                          file_extensions: List[str] = None,
                          max_depth: int = 5) -> List[str]:
        """Discover documents in directory tree"""
        if file_extensions is None:
            file_extensions = ['.pdf', '.txt', '.md', '.docx', '.html', '.py', '.js', '.ts', '.json']
        
        documents = []
        root = Path(root_path)
        
        for ext in file_extensions:
            pattern = f"**/*{ext}"
            for file_path in root.glob(pattern):
                if file_path.is_file() and file_path.stat().st_size > 0:
                    # Check depth
                    depth = len(file_path.relative_to(root).parts)
                    if depth <= max_depth:
                        documents.append(str(file_path))
        
        self.logger.info(f"Discovered {len(documents)} documents in {root_path}")
        return documents
    
    def create_ingestion_plan(self, 
                            documents: List[str], 
                            collection_name: str,
                            batch_size: int = 50) -> List[BatchJob]:
        """Create an optimized ingestion plan"""
        jobs = []
        
        # Group documents by type for specialized processing
        doc_types = {}
        for doc_path in documents:
            doc_type = self.processor.type_detector.detect_type(doc_path)
            if doc_type not in doc_types:
                doc_types[doc_type] = []
            doc_types[doc_type].append(doc_path)
        
        # Create specialized jobs for each document type
        for doc_type, type_docs in doc_types.items():
            # Split into batches
            for i in range(0, len(type_docs), batch_size):
                batch_docs = type_docs[i:i + batch_size]
                job_id = f"{collection_name}_{doc_type}_{i//batch_size + 1}"
                
                job = self.batch_manager.create_batch_job(
                    batch_docs, 
                    f"{collection_name}_{doc_type}",
                    job_id
                )
                jobs.append(job)
        
        self.logger.info(f"Created {len(jobs)} ingestion jobs")
        return jobs
    
    async def execute_ingestion_plan(self, jobs: List[BatchJob], max_concurrent: int = 3):
        """Execute the ingestion plan with controlled concurrency"""
        self.logger.info(f"Executing {len(jobs)} jobs with max {max_concurrent} concurrent")
        
        # Start jobs with concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_job(job: BatchJob):
            async with semaphore:
                self.batch_manager.start_batch_job(job.job_id)
                # Monitor job completion
                while True:
                    status = self.batch_manager.get_job_status(job.job_id)
                    if status and status['status'] in ['completed', 'failed', 'cancelled']:
                        break
                    await asyncio.sleep(5)
                return status
        
        # Execute all jobs
        tasks = [execute_job(job) for job in jobs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Report results
        completed = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'completed')
        failed = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'failed')
        
        self.logger.info(f"Ingestion complete: {completed} successful, {failed} failed")
        return results
    
    def optimize_collections(self, collection_names: List[str]):
        """Optimize existing collections for better performance"""
        self.logger.info(f"Optimizing {len(collection_names)} collections")
        
        for collection_name in collection_names:
            try:
                # Get collection stats
                stats = self.analytics.get_collection_stats(collection_name)
                if collection_name in stats:
                    stat = stats[collection_name]
                    
                    # Check for optimization opportunities
                    if stat['avg_quality_score'] < 0.7:
                        self.logger.warning(f"Low quality score for {collection_name}: {stat['avg_quality_score']:.3f}")
                    
                    if stat['total_errors'] > stat['total_documents'] * 0.1:
                        self.logger.warning(f"High error rate for {collection_name}: {stat['total_errors']} errors")
                    
                    # Generate optimization recommendations
                    recommendations = self._generate_optimization_recommendations(stat)
                    if recommendations:
                        self.logger.info(f"Optimization recommendations for {collection_name}:")
                        for rec in recommendations:
                            self.logger.info(f"  - {rec}")
                
            except Exception as e:
                self.logger.error(f"Error optimizing {collection_name}: {e}")
    
    def _generate_optimization_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on stats"""
        recommendations = []
        
        if stats['avg_quality_score'] < 0.7:
            recommendations.append("Consider improving document quality filtering")
        
        if stats['avg_processing_time'] > 60:
            recommendations.append("Consider using batch processing for better performance")
        
        if stats['total_errors'] > stats['total_documents'] * 0.05:
            recommendations.append("Review error logs and improve document preprocessing")
        
        if stats['total_chunks'] / stats['total_documents'] < 2:
            recommendations.append("Consider adjusting chunking strategy for better granularity")
        
        return recommendations
    
    def generate_comprehensive_report(self, collection_names: List[str] = None):
        """Generate a comprehensive ingestion report"""
        if collection_names is None:
            # Get all collections
            all_stats = self.analytics.get_collection_stats()
            collection_names = list(all_stats.keys())
        
        print("📊 Comprehensive Document Ingestion Report")
        print("=" * 60)
        print(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        
        # Overall statistics
        total_docs = 0
        total_chunks = 0
        total_errors = 0
        
        for collection_name in collection_names:
            stats = self.analytics.get_collection_stats(collection_name)
            if collection_name in stats:
                stat = stats[collection_name]
                total_docs += stat['total_documents']
                total_chunks += stat['total_chunks']
                total_errors += stat['total_errors']
        
        print(f"📈 Overall Statistics:")
        print(f"   Total Documents: {total_docs:,}")
        print(f"   Total Chunks: {total_chunks:,}")
        print(f"   Total Errors: {total_errors:,}")
        print(f"   Collections: {len(collection_names)}")
        print("")
        
        # Collection-specific reports
        for collection_name in collection_names:
            report = self.analytics.generate_performance_report(collection_name)
            print(report)
            print("")
        
        # Optimization recommendations
        print("🎯 Optimization Recommendations:")
        for collection_name in collection_names:
            stats = self.analytics.get_collection_stats(collection_name)
            if collection_name in stats:
                recommendations = self._generate_optimization_recommendations(stats[collection_name])
                if recommendations:
                    print(f"   {collection_name}:")
                    for rec in recommendations:
                        print(f"     - {rec}")
        
        print("")
        print("💡 Next Steps:")
        print("   1. Review optimization recommendations")
        print("   2. Monitor performance trends")
        print("   3. Consider adding more document sources")
        print("   4. Implement quality improvements")

def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description="Maximize Document Ingestion")
    parser.add_argument("--discover", type=str, help="Discover documents in directory")
    parser.add_argument("--collection", type=str, default="maximized_docs", help="Collection name")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing")
    parser.add_argument("--max-concurrent", type=int, default=3, help="Max concurrent jobs")
    parser.add_argument("--optimize", action="store_true", help="Optimize existing collections")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive report")
    parser.add_argument("--monitor", type=str, help="Monitor specific collection")
    
    args = parser.parse_args()
    
    maximizer = IngestionMaximizer()
    
    if args.discover:
        print(f"🔍 Discovering documents in: {args.discover}")
        documents = maximizer.discover_documents(args.discover)
        
        if documents:
            print(f"📄 Found {len(documents)} documents")
            
            # Create ingestion plan
            jobs = maximizer.create_ingestion_plan(documents, args.collection, args.batch_size)
            
            # Execute plan
            print(f"🚀 Executing ingestion plan with {len(jobs)} jobs")
            results = asyncio.run(maximizer.execute_ingestion_plan(jobs, args.max_concurrent))
            
            print("✅ Ingestion plan completed")
        else:
            print("❌ No documents found")
    
    elif args.optimize:
        print("🔧 Optimizing existing collections")
        # Get all collections
        all_stats = maximizer.analytics.get_collection_stats()
        collection_names = list(all_stats.keys())
        maximizer.optimize_collections(collection_names)
        print("✅ Optimization complete")
    
    elif args.report:
        print("📊 Generating comprehensive report")
        maximizer.generate_comprehensive_report()
    
    elif args.monitor:
        print(f"🔍 Starting monitoring for: {args.monitor}")
        monitor = IngestionMonitor(maximizer.analytics)
        monitor.start_monitoring(args.monitor)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()