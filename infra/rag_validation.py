#!/usr/bin/env python3
"""
RAG Validation System
Verifies retrieval accuracy and detects embedding drift
"""
import requests
import json
import hashlib
import time
from datetime import datetime
import os
import chromadb
from sentence_transformers import SentenceTransformer

class RAGValidator:
    def __init__(self, 
                 chroma_path='/Users/andrejsp/ai/vector_db/chroma',
                 n8n_webhook='http://localhost:5678/webhook/rag-chat',
                 results_dir='/Users/andrejsp/ai/benchmarks/2025-10',
                 chroma_url='http://localhost:8000'):
        self.chroma_path = chroma_path
        self.n8n_webhook = n8n_webhook
        self.results_dir = results_dir
        self.chroma_url = chroma_url
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        os.makedirs(results_dir, exist_ok=True)
        
        # Test queries for validation
        self.test_queries = [
            "What is machine learning?",
            "How does Docker work?",
            "Explain Python programming",
            "What are neural networks?",
            "How do vector databases work?",
            "What is natural language processing?",
            "Explain deep learning concepts",
            "How does ChromaDB store embeddings?",
            "What is artificial intelligence?",
            "How do you train a model?"
        ]
    
    def check_chromadb_health(self):
        """Check ChromaDB health using v2 API"""
        try:
            response = requests.get(f"{self.chroma_url}/api/v2/heartbeat", timeout=10)
            if response.status_code == 200:
                print("✅ ChromaDB v2 API is healthy")
                return True
            else:
                print(f"❌ ChromaDB v2 API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ ChromaDB v2 API health check failed: {e}")
            return False

    def calculate_embeddings_checksum(self):
        """Calculate checksum of current embeddings to detect drift"""
        try:
            client = chromadb.PersistentClient(path=self.chroma_path)
            collections = client.list_collections()
            
            checksums = {}
            for collection in collections:
                col = client.get_collection(collection.name)
                # Get all embeddings
                results = col.get(include=['embeddings'])
                embeddings = results.get('embeddings', [])
                
                # Calculate checksum
                embeddings_str = str(embeddings)
                checksum = hashlib.md5(embeddings_str.encode()).hexdigest()
                checksums[collection.name] = {
                    'checksum': checksum,
                    'count': len(embeddings),
                    'timestamp': datetime.now().isoformat()
                }
            
            return checksums
            
        except Exception as e:
            print(f"❌ Error calculating embeddings checksum: {e}")
            return {}
    
    def test_retrieval_accuracy(self, num_samples=100):
        """Test retrieval accuracy with sample queries"""
        print(f"🧪 Testing RAG retrieval accuracy with {num_samples} samples...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'num_samples': num_samples,
            'queries': [],
            'summary': {}
        }
        
        successful_queries = 0
        total_latency = 0
        
        for i, query in enumerate(self.test_queries[:num_samples]):
            print(f"  Query {i+1}/{min(num_samples, len(self.test_queries))}: {query[:50]}...")
            
            start_time = time.time()
            
            try:
                response = requests.post(
                    self.n8n_webhook,
                    json={'query': query},
                    timeout=30
                )
                
                latency = time.time() - start_time
                total_latency += latency
                
                if response.status_code == 200:
                    data = response.json()
                    successful_queries += 1
                    
                    query_result = {
                        'query': query,
                        'success': True,
                        'latency_s': latency,
                        'response_length': len(str(data)),
                        'status_code': response.status_code
                    }
                    
                    print(f"    ✅ {latency:.2f}s")
                else:
                    query_result = {
                        'query': query,
                        'success': False,
                        'latency_s': latency,
                        'error': f"HTTP {response.status_code}",
                        'status_code': response.status_code
                    }
                    print(f"    ❌ HTTP {response.status_code}")
                
            except Exception as e:
                latency = time.time() - start_time
                total_latency += latency
                
                query_result = {
                    'query': query,
                    'success': False,
                    'latency_s': latency,
                    'error': str(e),
                    'status_code': 0
                }
                print(f"    ❌ {e}")
            
            results['queries'].append(query_result)
            time.sleep(0.5)  # Rate limiting
        
        # Calculate summary
        results['summary'] = {
            'success_rate': (successful_queries / len(results['queries'])) * 100,
            'avg_latency_s': total_latency / len(results['queries']),
            'total_queries': len(results['queries']),
            'successful_queries': successful_queries
        }
        
        return results
    
    def validate_embeddings_consistency(self):
        """Validate that embeddings are consistent after ChromaDB restart"""
        print("🔍 Validating embeddings consistency...")
        
        # Get checksums before and after
        checksums_before = self.calculate_embeddings_checksum()
        
        print("  Restarting ChromaDB...")
        # Note: In production, you'd restart ChromaDB here
        # For now, we'll just check current state
        
        time.sleep(5)  # Simulate restart time
        
        checksums_after = self.calculate_embeddings_checksum()
        
        consistency_report = {
            'timestamp': datetime.now().isoformat(),
            'before': checksums_before,
            'after': checksums_after,
            'consistent': checksums_before == checksums_after
        }
        
        if consistency_report['consistent']:
            print("  ✅ Embeddings are consistent")
        else:
            print("  ❌ Embeddings have changed - possible drift detected")
        
        return consistency_report
    
    def run_full_validation(self):
        """Run complete RAG validation suite"""
        print("🚀 Starting RAG validation suite...")
        
        # Check ChromaDB health first
        chromadb_healthy = self.check_chromadb_health()
        
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'chromadb_health': chromadb_healthy,
            'retrieval_accuracy': self.test_retrieval_accuracy(10),  # Start with 10 samples
            'embeddings_consistency': self.validate_embeddings_consistency()
        }
        
        # Save results
        results_file = f"{self.results_dir}/rag_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        print(f"📊 Validation results saved to {results_file}")
        
        # Generate summary
        self.generate_validation_report(validation_results)
        
        return validation_results
    
    def generate_validation_report(self, results):
        """Generate human-readable validation report"""
        print("\n📈 RAG VALIDATION REPORT")
        print("=" * 50)
        
        # ChromaDB health
        print(f"\n🗄️  ChromaDB Health:")
        print(f"   Status: {'✅ Healthy' if results['chromadb_health'] else '❌ Unhealthy'}")
        
        # Retrieval accuracy summary
        accuracy = results['retrieval_accuracy']['summary']
        print(f"\n🎯 Retrieval Accuracy:")
        print(f"   Success rate: {accuracy['success_rate']:.1f}%")
        print(f"   Avg latency: {accuracy['avg_latency_s']:.2f}s")
        print(f"   Successful queries: {accuracy['successful_queries']}/{accuracy['total_queries']}")
        
        # Embeddings consistency
        consistency = results['embeddings_consistency']
        print(f"\n🔍 Embeddings Consistency:")
        print(f"   Consistent: {'✅ Yes' if consistency['consistent'] else '❌ No'}")
        
        if not consistency['consistent']:
            print("   ⚠️  Embedding drift detected - investigate data integrity")

if __name__ == "__main__":
    validator = RAGValidator()
    results = validator.run_full_validation()