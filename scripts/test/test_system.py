#!/usr/bin/env python3
"""
AI System Comprehensive Test Suite
Tests all components of the AI agent system
"""

import sys
import os
import json
import time
import subprocess
import requests
from datetime import datetime
from typing import Dict, Any, List

# Add scripts directory to path
sys.path.append('/Users/andrejsp/ai/scripts')

class AISystemTester:
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name: str, status: str, message: str = "", details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def test_python_environment(self):
        """Test Python environment and dependencies"""
        print("\n🐍 Testing Python Environment...")
        
        try:
            import torch
            self.log_test("PyTorch", "PASS", f"Version: {torch.__version__}")
        except ImportError as e:
            self.log_test("PyTorch", "FAIL", f"Not installed: {e}")
        
        try:
            import transformers
            self.log_test("Transformers", "PASS", f"Version: {transformers.__version__}")
        except ImportError as e:
            self.log_test("Transformers", "FAIL", f"Not installed: {e}")
        
        try:
            import chromadb
            self.log_test("ChromaDB", "PASS", f"Version: {chromadb.__version__}")
        except ImportError as e:
            self.log_test("ChromaDB", "FAIL", f"Not installed: {e}")
        
        try:
            import fastapi
            self.log_test("FastAPI", "PASS", f"Version: {fastapi.__version__}")
        except ImportError as e:
            self.log_test("FastAPI", "FAIL", f"Not installed: {e}")
    
    def test_scripts_existence(self):
        """Test that all required scripts exist"""
        print("\n📁 Testing Script Files...")
        
        required_scripts = [
            "rag_query.py",
            "ingest_documents.py", 
            "fine_tune_qlora.py",
            "evaluate_rag.py",
            "comprehensive_ingestion.py"
        ]
        
        for script in required_scripts:
            script_path = f"/Users/andrejsp/ai/scripts/{script}"
            if os.path.exists(script_path):
                self.log_test(f"Script {script}", "PASS", "File exists")
            else:
                self.log_test(f"Script {script}", "FAIL", "File not found")
    
    def test_config_files(self):
        """Test configuration files"""
        print("\n⚙️ Testing Configuration Files...")
        
        config_files = [
            "/Users/andrejsp/ai/configs/rag_config.json",
            "/Users/andrejsp/ai/configs/runtime.yaml"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                self.log_test(f"Config {os.path.basename(config_file)}", "PASS", "File exists")
            else:
                self.log_test(f"Config {os.path.basename(config_file)}", "FAIL", "File not found")
    
    def test_n8n_workflows(self):
        """Test n8n workflow files"""
        print("\n🔄 Testing n8n Workflows...")
        
        workflow_files = [
            "document_ingestion_workflow.json",
            "rag_query_workflow.json", 
            "monitoring_workflow.json",
            "production_rag_workflow.json"
        ]
        
        for workflow in workflow_files:
            workflow_path = f"/Users/andrejsp/ai/n8n/workflows/{workflow}"
            if os.path.exists(workflow_path):
                try:
                    with open(workflow_path, 'r') as f:
                        workflow_data = json.load(f)
                    
                    # Validate workflow structure
                    required_fields = ["name", "nodes", "connections"]
                    missing_fields = [field for field in required_fields if field not in workflow_data]
                    
                    if not missing_fields:
                        self.log_test(f"Workflow {workflow}", "PASS", f"Valid JSON with {len(workflow_data.get('nodes', []))} nodes")
                    else:
                        self.log_test(f"Workflow {workflow}", "FAIL", f"Missing fields: {missing_fields}")
                except json.JSONDecodeError as e:
                    self.log_test(f"Workflow {workflow}", "FAIL", f"Invalid JSON: {e}")
            else:
                self.log_test(f"Workflow {workflow}", "FAIL", "File not found")
    
    def test_docker_files(self):
        """Test Docker configuration files"""
        print("\n🐳 Testing Docker Configuration...")
        
        docker_files = [
            "docker-compose.yml",
            "docker-compose.override.yml",
            "requirements.txt",
            ".env.example"
        ]
        
        for docker_file in docker_files:
            file_path = f"/Users/andrejsp/ai/{docker_file}"
            if os.path.exists(file_path):
                self.log_test(f"Docker {docker_file}", "PASS", "File exists")
            else:
                self.log_test(f"Docker {docker_file}", "FAIL", "File not found")
        
        # Test Dockerfile directory
        dockerfiles = [
            "rag-api.Dockerfile",
            "training.Dockerfile", 
            "monitoring.Dockerfile",
            "web-interface.Dockerfile"
        ]
        
        for dockerfile in dockerfiles:
            dockerfile_path = f"/Users/andrejsp/ai/docker/{dockerfile}"
            if os.path.exists(dockerfile_path):
                self.log_test(f"Dockerfile {dockerfile}", "PASS", "File exists")
            else:
                self.log_test(f"Dockerfile {dockerfile}", "FAIL", "File not found")
    
    def test_api_integration(self):
        """Test API integration files"""
        print("\n🔌 Testing API Integration...")
        
        api_files = [
            "/Users/andrejsp/ai/n8n/api_integration.py",
            "/Users/andrejsp/ai/n8n/test_workflows.py",
            "/Users/andrejsp/ai/scripts/rag_api.py",
            "/Users/andrejsp/ai/scripts/monitoring_service.py"
        ]
        
        for api_file in api_files:
            if os.path.exists(api_file):
                self.log_test(f"API {os.path.basename(api_file)}", "PASS", "File exists")
            else:
                self.log_test(f"API {os.path.basename(api_file)}", "FAIL", "File not found")
    
    def test_directory_structure(self):
        """Test directory structure"""
        print("\n📂 Testing Directory Structure...")
        
        required_dirs = [
            "/Users/andrejsp/ai/scripts",
            "/Users/andrejsp/ai/n8n/workflows",
            "/Users/andrejsp/ai/docker",
            "/Users/andrejsp/ai/configs",
            "/Users/andrejsp/ai/vector_db",
            "/Users/andrejsp/ai/fine_tuned_models",
            "/Users/andrejsp/ai/sample_docs"
        ]
        
        for directory in required_dirs:
            if os.path.exists(directory) and os.path.isdir(directory):
                self.log_test(f"Directory {os.path.basename(directory)}", "PASS", "Directory exists")
            else:
                self.log_test(f"Directory {os.path.basename(directory)}", "FAIL", "Directory not found")
    
    def test_import_functionality(self):
        """Test importing key modules"""
        print("\n📦 Testing Module Imports...")
        
        try:
            from rag_query import query_rag_system
            self.log_test("RAG Query Import", "PASS", "Module imported successfully")
        except ImportError as e:
            self.log_test("RAG Query Import", "FAIL", f"Import failed: {e}")
        
        try:
            from ingest_documents import ingest_directory
            self.log_test("Document Ingestion Import", "PASS", "Module imported successfully")
        except ImportError as e:
            self.log_test("Document Ingestion Import", "FAIL", f"Import failed: {e}")
        
        try:
            from fine_tune_qlora import fine_tune_model
            self.log_test("Fine-tuning Import", "PASS", "Module imported successfully")
        except ImportError as e:
            self.log_test("Fine-tuning Import", "FAIL", f"Import failed: {e}")
    
    def test_ollama_availability(self):
        """Test if Ollama is available"""
        print("\n🤖 Testing Ollama Availability...")
        
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.log_test("Ollama Service", "PASS", f"Running with {len(models)} models")
            else:
                self.log_test("Ollama Service", "FAIL", f"HTTP {response.status_code}")
        except requests.RequestException as e:
            self.log_test("Ollama Service", "FAIL", f"Not accessible: {e}")
    
    def test_chromadb_availability(self):
        """Test if ChromaDB is available"""
        print("\n🗄️ Testing ChromaDB Availability...")
        
        try:
            response = requests.get("http://localhost:8000/api/v2/heartbeat", timeout=5)
            if response.status_code == 200:
                self.log_test("ChromaDB Service", "PASS", "Running and accessible")
            else:
                self.log_test("ChromaDB Service", "FAIL", f"HTTP {response.status_code}")
        except requests.RequestException as e:
            self.log_test("ChromaDB Service", "FAIL", f"Not accessible: {e}")
    
    def test_n8n_availability(self):
        """Test if n8n is available"""
        print("\n🔄 Testing n8n Availability...")
        
        try:
            response = requests.get("http://localhost:5678/api/v2/workflows", timeout=5)
            if response.status_code == 200:
                workflows = response.json().get('data', [])
                self.log_test("n8n Service", "PASS", f"Running with {len(workflows)} workflows")
            else:
                self.log_test("n8n Service", "FAIL", f"HTTP {response.status_code}")
        except requests.RequestException as e:
            self.log_test("n8n Service", "FAIL", f"Not accessible: {e}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        
        # Count results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        
        print("\n" + "="*60)
        print("📊 AI SYSTEM TEST REPORT")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print("="*60)
        
        # Show failed tests
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   • {result['test']}: {result['message']}")
        
        # Show warnings
        if warning_tests > 0:
            print("\n⚠️  WARNINGS:")
            for result in self.test_results:
                if result["status"] == "WARN":
                    print(f"   • {result['test']}: {result['message']}")
        
        # Save detailed report
        report_file = f"/Users/andrejsp/ai/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "total_time": total_time,
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return total_tests, passed_tests, failed_tests, warning_tests
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting AI System Comprehensive Test Suite")
        print("="*60)
        
        self.test_python_environment()
        self.test_scripts_existence()
        self.test_config_files()
        self.test_n8n_workflows()
        self.test_docker_files()
        self.test_api_integration()
        self.test_directory_structure()
        self.test_import_functionality()
        self.test_ollama_availability()
        self.test_chromadb_availability()
        self.test_n8n_availability()
        
        return self.generate_report()

def main():
    """Run the test suite"""
    tester = AISystemTester()
    total, passed, failed, warnings = tester.run_all_tests()
    
    if failed == 0:
        print("\n🎉 All tests passed! AI system is ready.")
        return 0
    else:
        print(f"\n⚠️  {failed} tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())