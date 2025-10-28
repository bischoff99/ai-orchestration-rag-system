#!/usr/bin/env python3
"""
Telemetry System for AI Components
Logs request latency, error rates, and performance metrics
"""
import requests
import time
import json
import logging
from datetime import datetime
import os
from collections import defaultdict, deque
import statistics

class TelemetryCollector:
    def __init__(self, log_file='/Users/andrejsp/ai/logs/telemetry.json'):
        self.log_file = log_file
        self.metrics = {
            'n8n_requests': deque(maxlen=1000),
            'ollama_requests': deque(maxlen=1000),
            'chromadb_requests': deque(maxlen=1000),
            'errors': defaultdict(int),
            'latency_stats': defaultdict(list)
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/Users/andrejsp/ai/logs/telemetry.log'),
                logging.StreamHandler()
            ]
        )
    
    def log_request(self, service, endpoint, method, status_code, latency, error=None):
        """Log a request with telemetry data"""
        timestamp = datetime.now().isoformat()
        
        request_data = {
            'timestamp': timestamp,
            'service': service,
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'latency_ms': latency * 1000,
            'error': error
        }
        
        # Store in memory
        self.metrics[f'{service}_requests'].append(request_data)
        self.metrics['latency_stats'][service].append(latency)
        
        if status_code >= 400 or error:
            self.metrics['errors'][f'{service}_{status_code}'] += 1
            logging.warning(f"❌ {service} {method} {endpoint} - {status_code} - {latency:.3f}s - {error}")
        else:
            logging.info(f"✅ {service} {method} {endpoint} - {status_code} - {latency:.3f}s")
        
        # Persist to file
        self._persist_metrics()
    
    def _persist_metrics(self):
        """Persist metrics to JSON file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'metrics': dict(self.metrics)
                }, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to persist metrics: {e}")
    
    def get_latency_stats(self, service):
        """Get latency statistics for a service"""
        latencies = self.metrics['latency_stats'][service]
        if not latencies:
            return None
        
        return {
            'count': len(latencies),
            'mean': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'p95': sorted(latencies)[int(len(latencies) * 0.95)],
            'p99': sorted(latencies)[int(len(latencies) * 0.99)],
            'min': min(latencies),
            'max': max(latencies)
        }
    
    def get_error_rate(self, service):
        """Get error rate for a service"""
        requests = list(self.metrics[f'{service}_requests'])
        if not requests:
            return 0
        
        error_count = sum(1 for req in requests if req['status_code'] >= 400)
        return (error_count / len(requests)) * 100
    
    def generate_report(self):
        """Generate telemetry report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        for service in ['n8n', 'ollama', 'chromadb']:
            latency_stats = self.get_latency_stats(service)
            error_rate = self.get_error_rate(service)
            
            report['services'][service] = {
                'latency_stats': latency_stats,
                'error_rate_percent': error_rate,
                'total_requests': len(self.metrics[f'{service}_requests'])
            }
        
        return report

# Decorator for automatic telemetry collection
def with_telemetry(service_name, telemetry_collector):
    """Decorator to automatically collect telemetry for function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            status_code = 200
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                status_code = 500
                raise
            finally:
                latency = time.time() - start_time
                telemetry_collector.log_request(
                    service=service_name,
                    endpoint=func.__name__,
                    method='FUNCTION',
                    status_code=status_code,
                    latency=latency,
                    error=error
                )
        
        return wrapper
    return decorator