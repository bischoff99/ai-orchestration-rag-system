#!/usr/bin/env python3
"""
AI System Monitoring Service
Monitors all AI services and provides health checks
"""

import time
import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIMonitoringService:
    def __init__(self):
        self.services = {
            "chromadb": {"url": "http://chromadb:8000/api/v2/heartbeat", "port": 8000},
            "ollama": {"url": "http://ollama:11434/api/tags", "port": 11434},
            "n8n": {"url": "http://n8n:5678/api/v2/workflows", "port": 5678},
            "rag-api": {"url": "http://rag-api:8001/health", "port": 8001}
        }
        self.monitoring_data = []
    
    def check_service_health(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of a single service"""
        try:
            start_time = time.time()
            response = requests.get(config["url"], timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "service": service_name,
                    "status": "healthy",
                    "response_time": response_time,
                    "error": None,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "service": service_name,
                    "status": "unhealthy",
                    "response_time": response_time,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "service": service_name,
                "status": "unhealthy",
                "response_time": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_all_services(self) -> Dict[str, Any]:
        """Check health of all services"""
        results = []
        
        for service_name, config in self.services.items():
            result = self.check_service_health(service_name, config)
            results.append(result)
            logger.info(f"Service {service_name}: {result['status']}")
        
        overall_status = "healthy" if all(r["status"] == "healthy" for r in results) else "unhealthy"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "services": results,
            "summary": {
                "total_services": len(results),
                "healthy_services": len([r for r in results if r["status"] == "healthy"]),
                "unhealthy_services": len([r for r in results if r["status"] == "unhealthy"])
            }
        }
    
    def test_rag_functionality(self) -> Dict[str, Any]:
        """Test RAG system functionality"""
        try:
            test_query = "What is machine learning?"
            response = requests.post(
                "http://rag-api:8001/api/search",
                json={
                    "query": test_query,
                    "collection": "default_docs",
                    "k": 3
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "test_query": test_query,
                    "response_time": response.elapsed.total_seconds(),
                    "error": None
                }
            else:
                return {
                    "status": "error",
                    "test_query": test_query,
                    "response_time": 0,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "test_query": test_query,
                "response_time": 0,
                "error": str(e)
            }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        health_check = self.check_all_services()
        rag_test = self.test_rag_functionality()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "health_check": health_check,
            "rag_test": rag_test,
            "alert_level": self.determine_alert_level(health_check, rag_test)
        }
        
        # Store in monitoring data
        self.monitoring_data.append(report)
        
        # Keep only last 100 reports
        if len(self.monitoring_data) > 100:
            self.monitoring_data = self.monitoring_data[-100:]
        
        return report
    
    def determine_alert_level(self, health_check: Dict, rag_test: Dict) -> str:
        """Determine alert level based on system status"""
        if health_check["overall_status"] == "unhealthy":
            return "critical"
        elif rag_test["status"] == "error":
            return "warning"
        elif health_check["summary"]["unhealthy_services"] > 0:
            return "warning"
        else:
            return "info"
    
    def save_report(self, report: Dict[str, Any]):
        """Save report to file"""
        report_file = f"/app/logs/monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {report_file}")
    
    def run_monitoring_loop(self, interval: int = 60):
        """Run continuous monitoring"""
        logger.info("Starting AI system monitoring service...")
        
        while True:
            try:
                report = self.generate_report()
                self.save_report(report)
                
                # Log alert if needed
                if report["alert_level"] in ["warning", "critical"]:
                    logger.warning(f"Alert Level: {report['alert_level']} - {report['health_check']['summary']}")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring service stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)

def main():
    """Main function"""
    monitoring_service = AIMonitoringService()
    
    # Run initial check
    report = monitoring_service.generate_report()
    monitoring_service.save_report(report)
    
    # Start continuous monitoring
    monitoring_service.run_monitoring_loop(interval=60)

if __name__ == "__main__":
    main()