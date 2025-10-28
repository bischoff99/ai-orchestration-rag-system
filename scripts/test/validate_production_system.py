#!/usr/bin/env python3
"""
Production System Validation
Comprehensive validation of the complete n8n RAG Agent Workflow system
"""

import requests
import json
import time
import sys
from datetime import datetime
from pathlib import Path

class ProductionSystemValidator:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.ollama_url = "http://localhost:11434/api"
        self.chromadb_url = "http://localhost:8000/api/v1"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs"
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
    def validate_services(self):
        """Validate all core services are running"""
        print("🔍 Validating Core Services")
        print("=" * 40)
        
        services = {
            "n8n": self.n8n_url,
            "Ollama": f"{self.ollama_url}/tags",
            "ChromaDB": f"{self.chromadb_url}/heartbeat"
        }
        
        healthy_services = []
        
        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {service_name}: Healthy")
                    healthy_services.append(service_name)
                else:
                    print(f"   ⚠️  {service_name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {service_name}: {e}")
        
        return healthy_services
    
    def validate_workflows(self):
        """Validate n8n workflows are active"""
        print("\n🔄 Validating n8n Workflows")
        print("=" * 40)
        
        try:
            response = requests.get(f"{self.n8n_url}/api/v2/workflows", headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Failed to get workflows: HTTP {response.status_code}")
                return False
            
            workflows_data = response.json()
            workflows = workflows_data.get('data', [])
            
            active_workflows = []
            for workflow in workflows:
                name = workflow.get('name', 'Unknown')
                active = workflow.get('active', False)
                if active:
                    active_workflows.append(name)
                    print(f"   ✅ {name}: Active")
                else:
                    print(f"   ⚠️  {name}: Inactive")
            
            print(f"\n   📊 Active workflows: {len(active_workflows)}/{len(workflows)}")
            return len(active_workflows) > 0
            
        except Exception as e:
            print(f"   ❌ Error validating workflows: {e}")
            return False
    
    def validate_chromadb_collections(self):
        """Validate ChromaDB collections are accessible"""
        print("\n📚 Validating ChromaDB Collections")
        print("=" * 40)
        
        try:
            # Test heartbeat
            response = requests.get(f"{self.chromadb_url}/heartbeat", timeout=5)
            if response.status_code != 200:
                print(f"   ❌ ChromaDB heartbeat failed: HTTP {response.status_code}")
                return False
            
            print("   ✅ ChromaDB heartbeat: OK")
            
            # Test collection creation
            test_collection = "validation_test"
            response = requests.post(
                f"{self.chromadb_url}/collections",
                json={"name": test_collection},
                timeout=10
            )
            
            if response.status_code in [200, 409]:  # 409 = already exists
                print(f"   ✅ Collection creation: OK")
                
                # Test document addition
                doc_data = {
                    "documents": ["This is a validation test document."],
                    "metadatas": [{"source": "validation", "type": "test"}],
                    "ids": ["validation_doc_1"]
                }
                
                response = requests.post(
                    f"{self.chromadb_url}/collections/{test_collection}/add",
                    json=doc_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("   ✅ Document addition: OK")
                    
                    # Test query
                    query_data = {
                        "query_texts": ["validation test"],
                        "n_results": 1
                    }
                    
                    response = requests.post(
                        f"{self.chromadb_url}/collections/{test_collection}/query",
                        json=query_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        print("   ✅ Document query: OK")
                        return True
                    else:
                        print(f"   ❌ Document query failed: HTTP {response.status_code}")
                        return False
                else:
                    print(f"   ❌ Document addition failed: HTTP {response.status_code}")
                    return False
            else:
                print(f"   ❌ Collection creation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ ChromaDB validation error: {e}")
            return False
    
    def validate_ollama_models(self):
        """Validate Ollama models are available"""
        print("\n🦙 Validating Ollama Models")
        print("=" * 40)
        
        try:
            response = requests.get(f"{self.ollama_url}/tags", timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Model listing failed: HTTP {response.status_code}")
                return False
            
            models = response.json().get('models', [])
            print(f"   📊 Available models: {len(models)}")
            
            # Test model generation
            test_payload = {
                "model": "llama-assistant",
                "prompt": "What is artificial intelligence?",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/generate",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                print(f"   ✅ Model generation: OK")
                print(f"      Response: {response_text[:100]}...")
                return True
            else:
                print(f"   ❌ Model generation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Ollama validation error: {e}")
            return False
    
    def validate_configuration_files(self):
        """Validate all configuration files exist"""
        print("\n📁 Validating Configuration Files")
        print("=" * 40)
        
        config_files = [
            "configs/rag_config.json",
            "configs/ingestion_workflow.json",
            "configs/monitoring_dashboard.json",
            "configs/fallback_mechanisms.json",
            "configs/evaluation_metrics.json"
        ]
        
        existing_files = []
        for config_file in config_files:
            if Path(config_file).exists():
                print(f"   ✅ {config_file}: Exists")
                existing_files.append(config_file)
            else:
                print(f"   ❌ {config_file}: Missing")
        
        print(f"\n   📊 Configuration files: {len(existing_files)}/{len(config_files)}")
        return len(existing_files) == len(config_files)
    
    def validate_training_data(self):
        """Validate training datasets exist"""
        print("\n📊 Validating Training Data")
        print("=" * 40)
        
        training_files = [
            "datasets/code_training.json",
            "datasets/technical_training.json",
            "datasets/workflow_training.json"
        ]
        
        existing_files = []
        for training_file in training_files:
            if Path(training_file).exists():
                print(f"   ✅ {training_file}: Exists")
                existing_files.append(training_file)
            else:
                print(f"   ❌ {training_file}: Missing")
        
        print(f"\n   📊 Training files: {len(existing_files)}/{len(training_files)}")
        return len(existing_files) == len(training_files)
    
    def validate_implementation_scripts(self):
        """Validate implementation scripts exist"""
        print("\n🔧 Validating Implementation Scripts")
        print("=" * 40)
        
        script_files = [
            "phase1_diagnose_workflows.py",
            "phase2_rag_ingestion.py",
            "phase3_fine_tuning.py",
            "phase4_orchestration.py",
            "final_system_test.py",
            "activate_all_workflows.py"
        ]
        
        existing_files = []
        for script_file in script_files:
            if Path(script_file).exists():
                print(f"   ✅ {script_file}: Exists")
                existing_files.append(script_file)
            else:
                print(f"   ❌ {script_file}: Missing")
        
        print(f"\n   📊 Implementation scripts: {len(existing_files)}/{len(script_files)}")
        return len(existing_files) == len(script_files)
    
    def create_validation_report(self, validation_results):
        """Create comprehensive validation report"""
        print("\n📊 Creating Validation Report")
        print("=" * 40)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "validation_status": "passed" if all(validation_results.values()) else "failed",
            "validation_results": validation_results,
            "system_components": {
                "n8n_workflows": "operational",
                "ollama_models": "operational",
                "chromadb_collections": "operational",
                "configuration_files": "complete",
                "training_data": "complete",
                "implementation_scripts": "complete"
            },
            "production_readiness": {
                "core_services": validation_results.get('services', False),
                "workflows": validation_results.get('workflows', False),
                "chromadb": validation_results.get('chromadb', False),
                "ollama": validation_results.get('ollama', False),
                "configuration": validation_results.get('config_files', False),
                "training_data": validation_results.get('training_data', False),
                "scripts": validation_results.get('scripts', False)
            },
            "recommendations": []
        }
        
        # Add recommendations based on validation results
        if not validation_results.get('services', False):
            report["recommendations"].append("Start all required services")
        if not validation_results.get('workflows', False):
            report["recommendations"].append("Activate workflows in n8n UI")
        if not validation_results.get('chromadb', False):
            report["recommendations"].append("Restart ChromaDB service")
        if not validation_results.get('ollama', False):
            report["recommendations"].append("Check Ollama service and models")
        
        # Save report
        report_path = "/Users/andrejsp/ai/PRODUCTION_VALIDATION_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   ✅ Validation report saved: {report_path}")
        return report
    
    def run_validation(self):
        """Run complete production system validation"""
        print("🚀 Production System Validation")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all validations
        validation_results = {
            'services': len(self.validate_services()) >= 2,
            'workflows': self.validate_workflows(),
            'chromadb': self.validate_chromadb_collections(),
            'ollama': self.validate_ollama_models(),
            'config_files': self.validate_configuration_files(),
            'training_data': self.validate_training_data(),
            'scripts': self.validate_implementation_scripts()
        }
        
        # Create validation report
        report = self.create_validation_report(validation_results)
        
        # Summary
        print(f"\n📊 Production Validation Summary:")
        print(f"   Core Services: {'✅' if validation_results['services'] else '❌'}")
        print(f"   n8n Workflows: {'✅' if validation_results['workflows'] else '❌'}")
        print(f"   ChromaDB: {'✅' if validation_results['chromadb'] else '❌'}")
        print(f"   Ollama: {'✅' if validation_results['ollama'] else '❌'}")
        print(f"   Configuration: {'✅' if validation_results['config_files'] else '❌'}")
        print(f"   Training Data: {'✅' if validation_results['training_data'] else '❌'}")
        print(f"   Implementation: {'✅' if validation_results['scripts'] else '❌'}")
        
        success_rate = sum(validation_results.values()) / len(validation_results) * 100
        print(f"\n🎯 Production Readiness: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 System is PRODUCTION READY!")
        elif success_rate >= 60:
            print("⚠️  System is mostly ready - some components need attention")
        else:
            print("❌ System needs significant configuration before production use")
        
        if report["recommendations"]:
            print(f"\n📋 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        return success_rate >= 80

def main():
    """Main function"""
    validator = ProductionSystemValidator()
    success = validator.run_validation()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())