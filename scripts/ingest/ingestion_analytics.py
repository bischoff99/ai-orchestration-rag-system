#!/usr/bin/env python3
"""
Ingestion Analytics Dashboard
Monitor and analyze document ingestion performance and quality
"""

import os
import sys
import time
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

@dataclass
class IngestionMetrics:
    """Track ingestion metrics over time"""
    timestamp: float
    collection_name: str
    documents_processed: int
    chunks_created: int
    processing_time: float
    quality_score_avg: float
    error_count: int
    file_types: Dict[str, int]

class IngestionAnalytics:
    """Analytics system for document ingestion monitoring"""
    
    def __init__(self, db_path: str = "/Users/andrejsp/ai/ingestion_analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingestion_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                collection_name TEXT NOT NULL,
                documents_processed INTEGER NOT NULL,
                chunks_created INTEGER NOT NULL,
                processing_time REAL NOT NULL,
                quality_score_avg REAL NOT NULL,
                error_count INTEGER NOT NULL,
                file_types TEXT NOT NULL
            )
        ''')
        
        # Create collections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at REAL NOT NULL,
                total_documents INTEGER DEFAULT 0,
                total_chunks INTEGER DEFAULT 0,
                last_updated REAL NOT NULL
            )
        ''')
        
        # Create quality_scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                collection_name TEXT NOT NULL,
                quality_score REAL NOT NULL,
                quality_details TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_metrics(self, metrics: IngestionMetrics):
        """Record ingestion metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ingestion_metrics 
            (timestamp, collection_name, documents_processed, chunks_created, 
             processing_time, quality_score_avg, error_count, file_types)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.timestamp,
            metrics.collection_name,
            metrics.documents_processed,
            metrics.chunks_created,
            metrics.processing_time,
            metrics.quality_score_avg,
            metrics.error_count,
            json.dumps(metrics.file_types)
        ))
        
        conn.commit()
        conn.close()
    
    def get_collection_stats(self, collection_name: str = None) -> Dict[str, Any]:
        """Get statistics for a collection or all collections"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if collection_name:
            cursor.execute('''
                SELECT 
                    collection_name,
                    SUM(documents_processed) as total_documents,
                    SUM(chunks_created) as total_chunks,
                    AVG(processing_time) as avg_processing_time,
                    AVG(quality_score_avg) as avg_quality_score,
                    SUM(error_count) as total_errors,
                    COUNT(*) as ingestion_sessions
                FROM ingestion_metrics 
                WHERE collection_name = ?
                GROUP BY collection_name
            ''', (collection_name,))
        else:
            cursor.execute('''
                SELECT 
                    collection_name,
                    SUM(documents_processed) as total_documents,
                    SUM(chunks_created) as total_chunks,
                    AVG(processing_time) as avg_processing_time,
                    AVG(quality_score_avg) as avg_quality_score,
                    SUM(error_count) as total_errors,
                    COUNT(*) as ingestion_sessions
                FROM ingestion_metrics 
                GROUP BY collection_name
                ORDER BY total_documents DESC
            ''')
        
        results = cursor.fetchall()
        conn.close()
        
        stats = {}
        for row in results:
            stats[row[0]] = {
                'total_documents': row[1],
                'total_chunks': row[2],
                'avg_processing_time': row[3],
                'avg_quality_score': row[4],
                'total_errors': row[5],
                'ingestion_sessions': row[6]
            }
        
        return stats
    
    def get_performance_trends(self, collection_name: str = None, days: int = 7) -> pd.DataFrame:
        """Get performance trends over time"""
        conn = sqlite3.connect(self.db_path)
        
        start_time = time.time() - (days * 24 * 60 * 60)
        
        if collection_name:
            query = '''
                SELECT timestamp, documents_processed, chunks_created, 
                       processing_time, quality_score_avg, error_count
                FROM ingestion_metrics 
                WHERE collection_name = ? AND timestamp > ?
                ORDER BY timestamp
            '''
            df = pd.read_sql_query(query, conn, params=(collection_name, start_time))
        else:
            query = '''
                SELECT timestamp, collection_name, documents_processed, 
                       chunks_created, processing_time, quality_score_avg, error_count
                FROM ingestion_metrics 
                WHERE timestamp > ?
                ORDER BY timestamp
            '''
            df = pd.read_sql_query(query, conn, params=(start_time,))
        
        conn.close()
        
        if not df.empty:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        return df
    
    def get_quality_analysis(self, collection_name: str = None) -> Dict[str, Any]:
        """Analyze document quality scores"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if collection_name:
            cursor.execute('''
                SELECT quality_score, quality_details
                FROM quality_scores 
                WHERE collection_name = ?
            ''', (collection_name,))
        else:
            cursor.execute('''
                SELECT quality_score, quality_details
                FROM quality_scores
            ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {}
        
        scores = [row[0] for row in results]
        quality_details = [json.loads(row[1]) for row in results]
        
        # Analyze quality issues
        issue_counts = {}
        for details in quality_details:
            for issue, count in details.items():
                if isinstance(count, bool) and count:
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1
                elif isinstance(count, (int, float)) and count > 0:
                    issue_counts[issue] = issue_counts.get(issue, 0) + count
        
        return {
            'score_distribution': {
                'min': min(scores),
                'max': max(scores),
                'mean': sum(scores) / len(scores),
                'median': sorted(scores)[len(scores) // 2]
            },
            'quality_issues': issue_counts,
            'total_documents': len(scores)
        }
    
    def generate_performance_report(self, collection_name: str = None) -> str:
        """Generate a comprehensive performance report"""
        stats = self.get_collection_stats(collection_name)
        trends = self.get_performance_trends(collection_name)
        quality = self.get_quality_analysis(collection_name)
        
        report = []
        report.append("📊 Document Ingestion Performance Report")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Collection statistics
        if collection_name and collection_name in stats:
            stat = stats[collection_name]
            report.append(f"📚 Collection: {collection_name}")
            report.append(f"   Total Documents: {stat['total_documents']:,}")
            report.append(f"   Total Chunks: {stat['total_chunks']:,}")
            report.append(f"   Avg Processing Time: {stat['avg_processing_time']:.2f}s")
            report.append(f"   Avg Quality Score: {stat['avg_quality_score']:.3f}")
            report.append(f"   Total Errors: {stat['total_errors']}")
            report.append(f"   Ingestion Sessions: {stat['ingestion_sessions']}")
        else:
            report.append("📚 All Collections Summary:")
            for name, stat in stats.items():
                report.append(f"   {name}: {stat['total_documents']:,} docs, "
                            f"{stat['total_chunks']:,} chunks, "
                            f"{stat['avg_quality_score']:.3f} avg quality")
        
        report.append("")
        
        # Quality analysis
        if quality:
            report.append("🎯 Quality Analysis:")
            dist = quality['score_distribution']
            report.append(f"   Score Range: {dist['min']:.3f} - {dist['max']:.3f}")
            report.append(f"   Average Score: {dist['mean']:.3f}")
            report.append(f"   Median Score: {dist['median']:.3f}")
            
            if quality['quality_issues']:
                report.append("   Common Issues:")
                for issue, count in sorted(quality['quality_issues'].items(), 
                                        key=lambda x: x[1], reverse=True):
                    report.append(f"     - {issue}: {count} documents")
        
        report.append("")
        
        # Performance trends
        if not trends.empty:
            report.append("📈 Recent Performance (7 days):")
            if 'datetime' in trends.columns:
                recent = trends.tail(5)
                for _, row in recent.iterrows():
                    report.append(f"   {row['datetime'].strftime('%Y-%m-%d %H:%M')}: "
                                f"{row['documents_processed']} docs, "
                                f"{row['chunks_created']} chunks, "
                                f"{row['quality_score_avg']:.3f} quality")
        
        return "\n".join(report)
    
    def create_performance_plots(self, collection_name: str = None, output_dir: str = "/Users/andrejsp/ai/analytics"):
        """Create performance visualization plots"""
        os.makedirs(output_dir, exist_ok=True)
        
        trends = self.get_performance_trends(collection_name)
        if trends.empty:
            print("No data available for plotting")
            return
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Document Ingestion Performance - {collection_name or "All Collections"}')
        
        # Documents processed over time
        if 'datetime' in trends.columns:
            axes[0, 0].plot(trends['datetime'], trends['documents_processed'], marker='o')
            axes[0, 0].set_title('Documents Processed Over Time')
            axes[0, 0].set_xlabel('Time')
            axes[0, 0].set_ylabel('Documents')
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Chunks created over time
        if 'datetime' in trends.columns:
            axes[0, 1].plot(trends['datetime'], trends['chunks_created'], marker='o', color='green')
            axes[0, 1].set_title('Chunks Created Over Time')
            axes[0, 1].set_xlabel('Time')
            axes[0, 1].set_ylabel('Chunks')
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Quality scores over time
        if 'datetime' in trends.columns:
            axes[1, 0].plot(trends['datetime'], trends['quality_score_avg'], marker='o', color='orange')
            axes[1, 0].set_title('Average Quality Score Over Time')
            axes[1, 0].set_xlabel('Time')
            axes[1, 0].set_ylabel('Quality Score')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Processing time over time
        if 'datetime' in trends.columns:
            axes[1, 1].plot(trends['datetime'], trends['processing_time'], marker='o', color='red')
            axes[1, 1].set_title('Processing Time Over Time')
            axes[1, 1].set_xlabel('Time')
            axes[1, 1].set_ylabel('Processing Time (s)')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save plot
        filename = f"performance_{collection_name or 'all'}_{int(time.time())}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Performance plots saved to: {filepath}")

class IngestionMonitor:
    """Real-time monitoring of ingestion processes"""
    
    def __init__(self, analytics: IngestionAnalytics):
        self.analytics = analytics
        self.monitoring = False
    
    def start_monitoring(self, collection_name: str, interval: int = 30):
        """Start real-time monitoring"""
        self.monitoring = True
        print(f"🔍 Starting monitoring for collection: {collection_name}")
        print(f"   Update interval: {interval} seconds")
        print("   Press Ctrl+C to stop")
        
        try:
            while self.monitoring:
                self._update_monitoring_display(collection_name)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped")
            self.monitoring = False
    
    def _update_monitoring_display(self, collection_name: str):
        """Update the monitoring display"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🔍 Real-time Ingestion Monitoring")
        print("=" * 40)
        print(f"Collection: {collection_name}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        
        # Get current stats
        stats = self.analytics.get_collection_stats(collection_name)
        if collection_name in stats:
            stat = stats[collection_name]
            print(f"📊 Current Statistics:")
            print(f"   Documents: {stat['total_documents']:,}")
            print(f"   Chunks: {stat['total_chunks']:,}")
            print(f"   Avg Quality: {stat['avg_quality_score']:.3f}")
            print(f"   Errors: {stat['total_errors']}")
            print(f"   Sessions: {stat['ingestion_sessions']}")
        
        print("")
        print("Press Ctrl+C to stop monitoring")

def main():
    """Test the analytics system"""
    print("📊 Ingestion Analytics Test")
    print("=" * 30)
    
    analytics = IngestionAnalytics()
    
    # Generate sample data
    sample_metrics = IngestionMetrics(
        timestamp=time.time(),
        collection_name="test_collection",
        documents_processed=100,
        chunks_created=500,
        processing_time=45.2,
        quality_score_avg=0.85,
        error_count=2,
        file_types={"pdf": 50, "txt": 30, "md": 20}
    )
    
    analytics.record_metrics(sample_metrics)
    
    # Generate report
    report = analytics.generate_performance_report("test_collection")
    print(report)
    
    # Create plots
    analytics.create_performance_plots("test_collection")

if __name__ == "__main__":
    main()