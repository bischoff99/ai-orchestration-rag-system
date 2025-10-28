#!/usr/bin/env python3
"""
Health Monitor for AI System Components - Fixed for ChromaDB v2 API
Monitors n8n, ChromaDB, and Ollama with automatic restart on failure
"""
import requests
import subprocess
import time
import logging
import json
from datetime import datetime
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/andrejsp/ai/logs/health_monitor.log'),
        logging.StreamHandler()
    ]
)

class HealthMonitor:
    def __init__(self):
        self.services = {
            'n8n': {
                'url': 'http://localhost:5678/healthz',
                'expected_status': 200,
                'launchctl_service': 'ai.n8n'
            },
            'chromadb': {
                'url': 'http://localhost:8000/api/v2/heartbeat',
                'expected_status': 200,  # Use v2 heartbeat endpoint
                'launchctl_service': 'ai.chromadb'
            },
            'ollama': {
                'url': 'http://localhost:11434/api/tags',
                'expected_status': 200,
                'launchctl_service': None  # Ollama runs as app
            }
        }
        self.restart_counts = {service: 0 for service in self.services}
        self.max_restarts = 3
    
    def check_service(self, service_name, config):
        """Check if a service is healthy"""
        try:
            response = requests.get(config['url'], timeout=10)
            if response.status_code == config['expected_status']:
                logging.info(f"✅ {service_name} is healthy")
                return True
            else:
                logging.warning(f"⚠️  {service_name} returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ {service_name} health check failed: {e}")
            return False
    
    def restart_service(self, service_name, config):
        """Restart a service using launchctl"""
        if not config['launchctl_service']:
            logging.warning(f"⚠️  {service_name} has no launchctl service configured")
            return False
            
        try:
            # Stop service
            subprocess.run(['launchctl', 'unload', f'~/Library/LaunchAgents/{config["launchctl_service"]}.plist'], 
                         check=False, capture_output=True)
            time.sleep(2)
            
            # Start service
            subprocess.run(['launchctl', 'load', f'~/Library/LaunchAgents/{config["launchctl_service"]}.plist'], 
                         check=True, capture_output=True)
            
            logging.info(f"🔄 Restarted {service_name}")
            self.restart_counts[service_name] += 1
            return True
            
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Failed to restart {service_name}: {e}")
            return False
    
    def run_health_check(self):
        """Run health check for all services"""
        logging.info("🔍 Starting health check cycle")
        
        for service_name, config in self.services.items():
            if not self.check_service(service_name, config):
                if self.restart_counts[service_name] < self.max_restarts:
                    logging.warning(f"🔄 Attempting to restart {service_name}")
                    if self.restart_service(service_name, config):
                        time.sleep(5)  # Wait for service to start
                        if not self.check_service(service_name, config):
                            logging.error(f"❌ {service_name} still unhealthy after restart")
                    else:
                        logging.error(f"❌ Failed to restart {service_name}")
                else:
                    logging.error(f"❌ {service_name} exceeded max restart attempts ({self.max_restarts})")
        
        # Log restart counts
        for service, count in self.restart_counts.items():
            if count > 0:
                logging.info(f"📊 {service} restarts: {count}")
    
    def run_continuous(self, interval=60):
        """Run health checks continuously"""
        logging.info(f"🚀 Starting continuous health monitoring (interval: {interval}s)")
        
        while True:
            try:
                self.run_health_check()
                time.sleep(interval)
            except KeyboardInterrupt:
                logging.info("🛑 Health monitoring stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Health monitor error: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    # Create logs directory
    os.makedirs('/Users/andrejsp/ai/logs', exist_ok=True)
    
    monitor = HealthMonitor()
    
    # Run single check or continuous monitoring
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        monitor.run_continuous()
    else:
        monitor.run_health_check()