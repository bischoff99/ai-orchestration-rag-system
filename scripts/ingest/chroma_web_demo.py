#!/usr/bin/env python3
"""
ChromaDB Web Demo
Show ChromaDB collections and data in a web-friendly format
"""

import sys
import json
from pathlib import Path

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from rag_setup import RAGVectorDB

def create_chroma_web_demo():
    """Create a web demo of ChromaDB data"""
    print("🌐 Creating ChromaDB Web Demo")
    print("=" * 35)
    
    # Initialize RAG system
    rag = RAGVectorDB(backend="chroma", collection_name="optimal_hf_datasets")
    
    # Get collection info
    collections = rag.client.list_collections()
    
    print(f"📊 Found {len(collections)} collections:")
    
    web_data = {
        "collections": [],
        "total_documents": 0,
        "demo_queries": [
            "What is machine learning?",
            "How do I write a Python function?",
            "Give me a creative writing prompt",
            "Solve: What is 15% of 200?",
            "Explain recursion in programming"
        ]
    }
    
    for collection in collections:
        collection_info = {
            "name": collection.name,
            "count": collection.count(),
            "metadata": collection.metadata,
            "sample_documents": []
        }
        
        # Get sample documents
        try:
            results = collection.get(limit=3)
            for i, doc in enumerate(results['documents']):
                collection_info["sample_documents"].append({
                    "text": doc[:200] + "..." if len(doc) > 200 else doc,
                    "metadata": results['metadatas'][i] if 'metadatas' in results else {}
                })
        except Exception as e:
            collection_info["error"] = str(e)
        
        web_data["collections"].append(collection_info)
        web_data["total_documents"] += collection.count()
        
        print(f"   - {collection.name}: {collection.count()} documents")
    
    # Test some queries
    print(f"\n🧪 Testing Demo Queries:")
    web_data["query_results"] = []
    
    for query in web_data["demo_queries"]:
        print(f"   Query: {query}")
        try:
            results = rag.search(query, k=3)
            query_result = {
                "query": query,
                "results": []
            }
            
            for result in results:
                query_result["results"].append({
                    "text": result["text"][:150] + "..." if len(result["text"]) > 150 else result["text"],
                    "score": round(result["distance"], 3),
                    "metadata": result["metadata"]
                })
            
            web_data["query_results"].append(query_result)
            print(f"      Found {len(results)} results")
            
        except Exception as e:
            print(f"      Error: {e}")
            web_data["query_results"].append({
                "query": query,
                "error": str(e)
            })
    
    # Save web data
    web_file = "/Users/andrejsp/ai/web/chroma_demo_data.json"
    with open(web_file, 'w') as f:
        json.dump(web_data, f, indent=2)
    
    print(f"\n✅ Web demo data saved to: {web_file}")
    
    # Create simple HTML viewer
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ChromaDB RAG System Demo</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .collection {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .query {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .result {{ margin: 5px 0; padding: 5px; background: white; border-left: 3px solid #007bff; }}
        .score {{ color: #666; font-size: 0.9em; }}
        .metadata {{ color: #888; font-size: 0.8em; }}
    </style>
</head>
<body>
    <h1>🚀 ChromaDB RAG System Demo</h1>
    
    <h2>📊 Collections ({web_data['total_documents']} total documents)</h2>
    {''.join([f'''
    <div class="collection">
        <h3>{col['name']} ({col['count']} documents)</h3>
        <p><strong>Metadata:</strong> {json.dumps(col.get('metadata', {}), indent=2)}</p>
        <h4>Sample Documents:</h4>
        {''.join([f'<div class="result"><p>{doc["text"]}</p><div class="metadata">{json.dumps(doc["metadata"], indent=2)}</div></div>' for doc in col.get('sample_documents', [])])}
    </div>
    ''' for col in web_data['collections']])}
    
    <h2>🧪 Demo Queries</h2>
    {''.join([f'''
    <div class="query">
        <h3>❓ {qr['query']}</h3>
        {''.join([f'<div class="result"><p>{result["text"]}</p><div class="score">Score: {result["score"]}</div><div class="metadata">{json.dumps(result["metadata"], indent=2)}</div></div>' for result in qr.get('results', [])]) if 'results' in qr else f'<p>Error: {qr.get("error", "Unknown error")}</p>'}
    </div>
    ''' for qr in web_data['query_results']])}
    
    <h2>💡 Usage</h2>
    <p>This demo shows your ChromaDB collections and sample queries. The actual web interface would be available at:</p>
    <ul>
        <li><strong>ChromaDB Admin:</strong> http://localhost:8000 (when server is running)</li>
        <li><strong>API Docs:</strong> http://localhost:8000/docs</li>
        <li><strong>Collections API:</strong> http://localhost:8000/api/v2/collections</li>
    </ul>
    
    <h2>🔧 Next Steps</h2>
    <ol>
        <li>Start ChromaDB server: <code>python /Users/andrejsp/ai/scripts/start_chroma_server.py</code></li>
        <li>Open http://localhost:8000 in your browser</li>
        <li>Browse collections and documents</li>
        <li>Use the API for programmatic access</li>
    </ol>
</body>
</html>
"""
    
    html_file = "/Users/andrejsp/ai/web/chroma_demo.html"
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"✅ HTML demo created: {html_file}")
    print(f"\n🌐 Open in browser: file://{html_file}")
    
    return web_data

def main():
    """Main function"""
    web_data = create_chroma_web_demo()
    
    print(f"\n🎉 ChromaDB Web Demo Complete!")
    print(f"\n📊 Summary:")
    print(f"   - Collections: {len(web_data['collections'])}")
    print(f"   - Total Documents: {web_data['total_documents']}")
    print(f"   - Demo Queries: {len(web_data['demo_queries'])}")
    
    print(f"\n🌐 Web Interfaces Available:")
    print(f"   1. HTML Demo: file:///Users/andrejsp/ai/web/chroma_demo.html")
    print(f"   2. ChromaDB Admin: http://localhost:8000 (start server first)")
    print(f"   3. API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()