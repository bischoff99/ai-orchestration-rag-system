#!/usr/bin/env python3
"""
Test All RAG Collections
Comprehensive testing of all collections with domain-specific queries
"""

import sys
import time
from typing import Dict, List, Any

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from rag_setup import RAGVectorDB

class CollectionTester:
    """Test all RAG collections with domain-specific queries"""
    
    def __init__(self):
        self.collections = {
            "coding_knowledge": {
                "description": "Programming and code-related content",
                "queries": [
                    "How do I write a Python function?",
                    "What are the best practices for JavaScript?",
                    "Explain object-oriented programming",
                    "How to implement a sorting algorithm?",
                    "What is memory management in programming?"
                ]
            },
            "general_knowledge": {
                "description": "General knowledge and Wikipedia content",
                "queries": [
                    "What is the history of artificial intelligence?",
                    "Explain quantum computing",
                    "What are the benefits of renewable energy?",
                    "How does the human brain work?",
                    "What is climate change?"
                ]
            },
            "technical_docs": {
                "description": "Technical documentation and guides",
                "queries": [
                    "How to set up Docker containers?",
                    "What is Kubernetes architecture?",
                    "How to design RESTful APIs?",
                    "What are ML pipeline best practices?",
                    "How to implement CI/CD?"
                ]
            },
            "reasoning_data": {
                "description": "Math reasoning and problem-solving",
                "queries": [
                    "Solve: What is 25% of 400?",
                    "How to calculate compound interest?",
                    "What is the area of a circle with radius 5?",
                    "Solve: 2x + 5 = 15",
                    "How to calculate standard deviation?"
                ]
            },
            "ai_ml_knowledge": {
                "description": "AI and machine learning content",
                "queries": [
                    "What is deep learning?",
                    "How do neural networks work?",
                    "What is MLOps?",
                    "Explain machine learning algorithms",
                    "What are the types of machine learning?"
                ]
            },
            "devops_knowledge": {
                "description": "DevOps and infrastructure content",
                "queries": [
                    "What is Kubernetes?",
                    "How to design CI/CD pipelines?",
                    "What is Infrastructure as Code?",
                    "How to implement blue-green deployment?",
                    "What are container orchestration best practices?"
                ]
            },
            "security_knowledge": {
                "description": "Cybersecurity and security content",
                "queries": [
                    "What are OWASP top 10 security risks?",
                    "What is zero trust security?",
                    "How to implement secure coding practices?",
                    "What is authentication vs authorization?",
                    "How to prevent SQL injection attacks?"
                ]
            },
            "data_science_knowledge": {
                "description": "Data science and analytics content",
                "queries": [
                    "How to analyze data with pandas?",
                    "What is data visualization?",
                    "How to handle missing data?",
                    "What is statistical significance?",
                    "How to build a data pipeline?"
                ]
            }
        }
    
    def test_collection(self, collection_name: str, queries: List[str]) -> Dict[str, Any]:
        """Test a specific collection with queries"""
        print(f"\n🔍 Testing Collection: {collection_name}")
        print("=" * 50)
        
        try:
            rag = RAGVectorDB(backend="chroma", collection_name=collection_name)
            
            # Get collection info
            collections = rag.client.list_collections()
            collection_info = None
            for collection in collections:
                if collection.name == collection_name:
                    collection_info = collection
                    break
            
            if not collection_info:
                print(f"❌ Collection '{collection_name}' not found")
                return {"error": "Collection not found"}
            
            doc_count = collection_info.count()
            print(f"📊 Documents in collection: {doc_count}")
            
            if doc_count == 0:
                print("⚠️  Collection is empty")
                return {"doc_count": 0, "queries_tested": 0}
            
            # Test queries
            results = {
                "collection_name": collection_name,
                "doc_count": doc_count,
                "queries_tested": 0,
                "successful_queries": 0,
                "average_results": 0,
                "query_results": []
            }
            
            total_results = 0
            
            for i, query in enumerate(queries, 1):
                print(f"\n❓ Query {i}: {query}")
                
                try:
                    search_results = rag.search(query, k=3)
                    
                    if search_results:
                        results["successful_queries"] += 1
                        total_results += len(search_results)
                        
                        print(f"   ✅ Found {len(search_results)} results")
                        
                        # Show best result
                        best_result = search_results[0]
                        print(f"   📄 Best match: {best_result['text'][:100]}...")
                        print(f"   📊 Score: {best_result['distance']:.3f}")
                        
                        results["query_results"].append({
                            "query": query,
                            "results_found": len(search_results),
                            "best_score": best_result['distance'],
                            "success": True
                        })
                    else:
                        print(f"   ❌ No results found")
                        results["query_results"].append({
                            "query": query,
                            "results_found": 0,
                            "success": False
                        })
                    
                    results["queries_tested"] += 1
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    results["query_results"].append({
                        "query": query,
                        "error": str(e),
                        "success": False
                    })
                    results["queries_tested"] += 1
            
            # Calculate average results
            if results["queries_tested"] > 0:
                results["average_results"] = total_results / results["queries_tested"]
            
            return results
            
        except Exception as e:
            print(f"❌ Error testing collection '{collection_name}': {e}")
            return {"error": str(e)}
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all collections"""
        print("🧪 Comprehensive RAG Collection Testing")
        print("=" * 50)
        
        start_time = time.time()
        all_results = {}
        
        for collection_name, config in self.collections.items():
            results = self.test_collection(collection_name, config["queries"])
            all_results[collection_name] = results
        
        # Calculate overall statistics
        end_time = time.time()
        duration = end_time - start_time
        
        total_collections = len(self.collections)
        successful_collections = sum(1 for r in all_results.values() if "error" not in r and r.get("doc_count", 0) > 0)
        total_documents = sum(r.get("doc_count", 0) for r in all_results.values())
        total_queries = sum(r.get("queries_tested", 0) for r in all_results.values())
        successful_queries = sum(r.get("successful_queries", 0) for r in all_results.values())
        
        print(f"\n🎉 Comprehensive Testing Complete!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Overall Statistics:")
        print(f"   - Collections Tested: {total_collections}")
        print(f"   - Successful Collections: {successful_collections}")
        print(f"   - Total Documents: {total_documents}")
        print(f"   - Total Queries: {total_queries}")
        print(f"   - Successful Queries: {successful_queries}")
        print(f"   - Success Rate: {(successful_queries/total_queries*100):.1f}%" if total_queries > 0 else "   - Success Rate: N/A")
        
        # Show collection summary
        print(f"\n📚 Collection Summary:")
        for collection_name, results in all_results.items():
            if "error" not in results:
                doc_count = results.get("doc_count", 0)
                success_rate = (results.get("successful_queries", 0) / results.get("queries_tested", 1)) * 100
                print(f"   - {collection_name}: {doc_count} docs, {success_rate:.1f}% success")
            else:
                print(f"   - {collection_name}: Error - {results['error']}")
        
        return all_results

def main():
    """Main function"""
    print("🎯 RAG Collection Comprehensive Testing")
    print("=" * 40)
    
    # Initialize tester
    tester = CollectionTester()
    
    # Run comprehensive test
    results = tester.run_comprehensive_test()
    
    print(f"\n💡 Recommendations:")
    print(f"1. 🌐 View collections: python /Users/andrejsp/ai/scripts/start_web_interfaces.py")
    print(f"2. 🔍 Focus on collections with high success rates")
    print(f"3. 📊 Add more documents to collections with low success rates")
    print(f"4. 🎯 Use specialized collections for domain-specific queries")

if __name__ == "__main__":
    main()