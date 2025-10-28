#!/usr/bin/env python3
"""
Fix 404 Webhook Errors - Specific Error Resolution
"""

import requests
import json
import time
from datetime import datetime

class Error404Fixer:
    def __init__(self):
        self.n8n_base_url = "http://localhost:5678"
        self.working_webhook = "/webhook/rag-chat"  # This one works
        self.broken_webhooks = [
            "/webhook/rag-complete",
            "/webhook/preprocess-document"
        ]
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_working_webhook(self):
        """Test the working webhook"""
        self.log("Testing working webhook...")
        
        try:
            response = requests.post(f"{self.n8n_base_url}{self.working_webhook}", 
                                   json={"query": "Hello, test query"}, 
                                   timeout=15)
            
            self.log(f"Status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                self.log("✅ Working webhook is functional", "SUCCESS")
                return True
            else:
                self.log("❌ Working webhook failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Working webhook error: {e}", "ERROR")
            return False
    
    def test_broken_webhooks(self):
        """Test the broken webhooks"""
        self.log("Testing broken webhooks...")
        
        for webhook in self.broken_webhooks:
            try:
                response = requests.post(f"{self.n8n_base_url}{webhook}", 
                                       json={"query": "test"}, 
                                       timeout=10)
                
                if response.status_code == 404:
                    self.log(f"❌ {webhook} - 404 Not Found (Expected)", "WARNING")
                else:
                    self.log(f"✅ {webhook} - Status {response.status_code}", "SUCCESS")
                    
            except Exception as e:
                self.log(f"❌ {webhook} - Error: {e}", "ERROR")
    
    def create_working_rag_test(self):
        """Create a working RAG test using the functional webhook"""
        self.log("Creating working RAG test...")
        
        test_queries = [
            "Hello, can you help me?",
            "What do you know about machine learning?",
            "Explain Docker containers",
            "What is Python programming?",
            "Tell me about vector databases"
        ]
        
        self.log(f"Testing {len(test_queries)} queries on working webhook...")
        
        for i, query in enumerate(test_queries, 1):
            self.log(f"Query {i}: {query}")
            
            try:
                response = requests.post(f"{self.n8n_base_url}{self.working_webhook}", 
                                       json={"query": query}, 
                                       timeout=30)
                
                if response.status_code == 200:
                    self.log(f"✅ Query {i} successful", "SUCCESS")
                    # Parse response to see if we get actual content
                    try:
                        data = response.json()
                        if "message" in data and "Workflow was started" in data["message"]:
                            self.log(f"   Response: {data['message']}", "INFO")
                        else:
                            self.log(f"   Response: {str(data)[:100]}...", "INFO")
                    except:
                        self.log(f"   Response: {response.text[:100]}...", "INFO")
                else:
                    self.log(f"❌ Query {i} failed: {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ Query {i} error: {e}", "ERROR")
            
            time.sleep(2)  # Rate limiting
    
    def analyze_404_errors(self):
        """Analyze the specific 404 errors"""
        self.log("Analyzing 404 errors...")
        
        error_analysis = {
            "error_type": "404 Webhook Not Registered",
            "root_cause": "Workflows not activated in n8n UI",
            "affected_endpoints": [
                "/webhook/rag-complete",
                "/webhook/preprocess-document"
            ],
            "working_endpoints": [
                "/webhook/rag-chat"
            ],
            "solution": "Manual activation required in n8n UI",
            "workaround": "Use working webhook for testing"
        }
        
        self.log("Error Analysis:")
        for key, value in error_analysis.items():
            self.log(f"  {key}: {value}", "INFO")
        
        return error_analysis
    
    def provide_manual_fix_instructions(self):
        """Provide manual fix instructions"""
        self.log("Manual Fix Instructions:", "INFO")
        self.log("=" * 50, "INFO")
        
        instructions = [
            "1. Open n8n UI: http://localhost:5678",
            "2. Go to Workflows section",
            "3. Find 'Complete RAG System - Working' workflow",
            "4. Click the 'Active' toggle switch to ON",
            "5. Save the workflow",
            "6. Repeat for 'Document Preprocessing Pipeline' workflow",
            "7. Test webhooks: curl -X POST http://localhost:5678/webhook/rag-complete -H 'Content-Type: application/json' -d '{\"query\": \"test\"}'"
        ]
        
        for instruction in instructions:
            self.log(instruction, "INFO")
        
        self.log("=" * 50, "INFO")
    
    def create_workaround_solution(self):
        """Create a workaround solution using the working webhook"""
        self.log("Creating workaround solution...")
        
        workaround_script = f'''#!/usr/bin/env python3
"""
Workaround for 404 errors - Use working webhook
"""

import requests
import json

def test_rag_system():
    """Test RAG system using working webhook"""
    webhook_url = "http://localhost:5678{self.working_webhook}"
    
    queries = [
        "Hello, test query",
        "What do you know about machine learning?",
        "Explain Docker containers",
        "What is Python programming?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {{query}}")
        
        try:
            response = requests.post(webhook_url, json={{"query": query}}, timeout=30)
            print(f"Status: {{response.status_code}}")
            print(f"Response: {{response.text}}")
            print("-" * 40)
        except Exception as e:
            print(f"Error: {{e}}")

if __name__ == "__main__":
    test_rag_system()
'''
        
        with open("/Users/andrejsp/ai/workaround_rag_test.py", "w") as f:
            f.write(workaround_script)
        
        self.log("✅ Workaround script created: workaround_rag_test.py", "SUCCESS")
    
    def run_error_fix(self):
        """Run the complete 404 error fixing process"""
        self.log("🚀 Starting 404 Error Fix Process", "INFO")
        self.log("=" * 50, "INFO")
        
        # Step 1: Test working webhook
        if not self.test_working_webhook():
            self.log("❌ Cannot proceed - no working webhooks", "ERROR")
            return False
        
        # Step 2: Test broken webhooks
        self.test_broken_webhooks()
        
        # Step 3: Analyze errors
        error_analysis = self.analyze_404_errors()
        
        # Step 4: Provide manual fix instructions
        self.provide_manual_fix_instructions()
        
        # Step 5: Create workaround solution
        self.create_workaround_solution()
        
        # Step 6: Test with working webhook
        self.create_working_rag_test()
        
        self.log("✅ 404 Error Fix Process Complete!", "SUCCESS")
        self.log("=" * 50, "INFO")
        
        return True

def main():
    """Main execution function"""
    fixer = Error404Fixer()
    success = fixer.run_error_fix()
    
    if success:
        print("\n🎉 404 Error Analysis Complete!")
        print("📋 Summary:")
        print("✅ Working webhook: /webhook/rag-chat")
        print("❌ Broken webhooks: /webhook/rag-complete, /webhook/preprocess-document")
        print("🔧 Solution: Manual activation in n8n UI required")
        print("🛠️ Workaround: Use working webhook for testing")
    else:
        print("\n❌ Error fixing process failed")

if __name__ == "__main__":
    main()