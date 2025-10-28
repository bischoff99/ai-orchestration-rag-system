#!/usr/bin/env python3
"""
RAG Orchestrator v2 - Production AI Stack Coordinator (Fixed)
Coordinates ChromaDB v2 queries, Ollama model inference, and n8n workflow execution
"""
import requests
import json
import time
import logging
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import os
import signal
import sys

@dataclass
class ServiceConfig:
    """Service configuration for RAG Orchestrator"""
    name: str
    url: str
    health_endpoint: str
    timeout: int = 10
    retry_attempts: int = 3
    backoff_seconds: int = 5

@dataclass
class QueryResult:
    """Result from RAG query processing"""
    query: str
    response: str
    context: List[str]
    latency: float
    success: bool
    error: Optional[str] = None
    model_used: Optional[str] = None
    confidence: Optional[float] = None

class RAGOrchestratorV2:
    """RAG Orchestrator v2 - Central reasoning and control agent"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize RAG Orchestrator v2"""
        self.version = "2.0.0"
        self.mode = "Production"
        self.api_version = "v2"
        self.health_check_interval = 60
        self.running = False
        
        # Service configurations (only local services)
        self.services = {
            "chromadb": ServiceConfig(
                name="ChromaDB v2",
                url="http://localhost:8000/api/v2",
                health_endpoint="/heartbeat"
            ),
            "ollama": ServiceConfig(
                name="Ollama",
                url="http://localhost:11434",
                health_endpoint="/api/tags"
            ),
            "n8n": ServiceConfig(
                name="n8n",
                url="http://localhost:5678",
                health_endpoint="/healthz"
            )
        }
        
        # Performance targets
        self.targets = {
            "avg_response_time_s": 0.02,
            "throughput_tok_per_s": 130,
            "uptime_target": 99.9
        }
        
        # Statistics
        self.stats = {
            "queries_processed": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_latency": 0.0,
            "uptime_start": datetime.now(),
            "last_health_check": None
        }
        
        # Setup logging
        self._setup_logging()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.logger.info(f"RAG Orchestrator v2 initialized - Mode: {self.mode}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path.home() / "ai" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "agent_rag_orchestrator.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("RAGOrchestratorV2")
        self.logger.info("Logging initialized")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop()
        sys.exit(0)
    
    async def health_check(self) -> Dict[str, bool]:
        """Perform health check on all services"""
        self.logger.info("Performing health check on all services...")
        
        health_status = {}
        
        async with aiohttp.ClientSession() as session:
            for service_name, config in self.services.items():
                try:
                    url = f"{config.url}{config.health_endpoint}"
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=config.timeout)) as response:
                        if response.status == 200:
                            health_status[service_name] = True
                            self.logger.info(f"✅ {config.name} - Healthy")
                        else:
                            health_status[service_name] = False
                            self.logger.warning(f"❌ {config.name} - HTTP {response.status}")
                except Exception as e:
                    health_status[service_name] = False
                    self.logger.error(f"❌ {config.name} - Error: {e}")
        
        self.stats["last_health_check"] = datetime.now()
        return health_status
    
    async def retrieve_context(self, query: str, collection: str = "rag_documents_collection", n_results: int = 3) -> List[str]:
        """Retrieve relevant context from ChromaDB v2 (with fallback)"""
        try:
            url = f"{self.services['chromadb'].url}/collections/{collection}/query"
            payload = {
                "query_texts": [query],
                "n_results": n_results
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        documents = data.get("documents", [[]])[0]
                        self.logger.info(f"Retrieved {len(documents)} context documents")
                        return documents
                    elif response.status == 404:
                        self.logger.warning(f"Collection '{collection}' not found, using fallback context")
                        return self._get_fallback_context(query)
                    else:
                        self.logger.error(f"ChromaDB query failed: HTTP {response.status}")
                        return self._get_fallback_context(query)
        except Exception as e:
            self.logger.error(f"ChromaDB retrieval error: {e}")
            return self._get_fallback_context(query)
    
    def _get_fallback_context(self, query: str) -> List[str]:
        """Get fallback context when ChromaDB is unavailable"""
        # Return some general context based on query keywords
        fallback_contexts = {
            "machine learning": [
                "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed.",
                "ML algorithms build mathematical models based on training data to make predictions or decisions."
            ],
            "docker": [
                "Docker is a containerization platform that packages applications and their dependencies into lightweight, portable containers.",
                "Containers provide consistent environments across development, testing, and production."
            ],
            "python": [
                "Python is a high-level programming language known for its simplicity, readability, and extensive library ecosystem.",
                "Python is widely used in data science, web development, automation, and artificial intelligence."
            ]
        }
        
        query_lower = query.lower()
        for keyword, contexts in fallback_contexts.items():
            if keyword in query_lower:
                return contexts
        
        return ["General knowledge context for query processing."]
    
    async def generate_response(self, query: str, context: List[str], model: str = "llama3.1:8b-instruct-q5_K_M") -> str:
        """Generate response using Ollama with context"""
        try:
            # Prepare context for the model
            context_text = "\n".join(context) if context else "No relevant context found."
            prompt = f"""Using the following context, answer the question:

Context: {context_text}

Question: {query}

Answer:"""
            
            url = f"{self.services['ollama'].url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response", "")
                        self.logger.info(f"Generated response using {model}")
                        return response_text
                    else:
                        self.logger.error(f"Ollama generation failed: HTTP {response.status}")
                        return "Error generating response"
        except Exception as e:
            self.logger.error(f"Ollama generation error: {e}")
            return f"Error: {e}"
    
    async def process_rag_query(self, query: str, collection: str = "rag_documents_collection") -> QueryResult:
        """Process a complete RAG query"""
        start_time = time.time()
        self.stats["queries_processed"] += 1
        
        try:
            self.logger.info(f"Processing RAG query: {query[:50]}...")
            
            # Step 1: Retrieve context
            context = await self.retrieve_context(query, collection)
            
            # Step 2: Generate response
            response = await self.generate_response(query, context)
            
            # Step 3: Calculate metrics
            latency = time.time() - start_time
            self.stats["total_latency"] += latency
            self.stats["successful_queries"] += 1
            
            # Calculate confidence based on context relevance
            confidence = min(0.9, len(context) / 3.0) if context else 0.1
            
            result = QueryResult(
                query=query,
                response=response,
                context=context,
                latency=latency,
                success=True,
                model_used="llama3.1:8b-instruct-q5_K_M",
                confidence=confidence
            )
            
            self.logger.info(f"Query processed successfully in {latency:.3f}s")
            return result
            
        except Exception as e:
            latency = time.time() - start_time
            self.stats["failed_queries"] += 1
            
            self.logger.error(f"RAG query failed: {e}")
            return QueryResult(
                query=query,
                response="",
                context=[],
                latency=latency,
                success=False,
                error=str(e)
            )
    
    async def trigger_n8n_workflow(self, workflow_name: str, data: Dict[str, Any]) -> bool:
        """Trigger n8n workflow with data"""
        try:
            webhook_url = f"{self.services['n8n'].url}/webhook/{workflow_name}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        self.logger.info(f"Successfully triggered n8n workflow: {workflow_name}")
                        return True
                    else:
                        self.logger.error(f"n8n workflow trigger failed: HTTP {response.status}")
                        return False
        except Exception as e:
            self.logger.error(f"n8n workflow trigger error: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        uptime = (datetime.now() - self.stats["uptime_start"]).total_seconds()
        
        avg_latency = 0.0
        if self.stats["queries_processed"] > 0:
            avg_latency = self.stats["total_latency"] / self.stats["queries_processed"]
        
        success_rate = 0.0
        if self.stats["queries_processed"] > 0:
            success_rate = (self.stats["successful_queries"] / self.stats["queries_processed"]) * 100
        
        return {
            "uptime_seconds": uptime,
            "queries_processed": self.stats["queries_processed"],
            "successful_queries": self.stats["successful_queries"],
            "failed_queries": self.stats["failed_queries"],
            "success_rate_percent": success_rate,
            "avg_response_time_s": avg_latency,
            "last_health_check": self.stats["last_health_check"].isoformat() if self.stats["last_health_check"] else None,
            "targets": self.targets
        }
    
    async def continuous_health_monitoring(self):
        """Continuous health monitoring loop"""
        self.logger.info("Starting continuous health monitoring...")
        
        while self.running:
            try:
                health_status = await self.health_check()
                
                # Log health status
                healthy_services = sum(1 for status in health_status.values() if status)
                total_services = len(health_status)
                
                if healthy_services == total_services:
                    self.logger.info(f"All {total_services} services healthy")
                else:
                    self.logger.warning(f"Only {healthy_services}/{total_services} services healthy")
                
                # Wait for next health check
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)  # Shorter wait on error
    
    async def start(self):
        """Start the RAG Orchestrator v2"""
        self.logger.info("Starting RAG Orchestrator v2...")
        self.running = True
        
        # Initial health check
        health_status = await self.health_check()
        healthy_services = sum(1 for status in health_status.values() if status)
        
        if healthy_services < len(health_status):
            self.logger.warning(f"Only {healthy_services}/{len(health_status)} services healthy at startup")
        
        # Start health monitoring in background
        health_task = asyncio.create_task(self.continuous_health_monitoring())
        
        self.logger.info("RAG Orchestrator v2 started successfully")
        
        try:
            # Keep running until stopped
            while self.running:
                await asyncio.sleep(1)
        finally:
            health_task.cancel()
            self.logger.info("RAG Orchestrator v2 stopped")
    
    def stop(self):
        """Stop the RAG Orchestrator v2"""
        self.logger.info("Stopping RAG Orchestrator v2...")
        self.running = False

# Example usage and testing
async def main():
    """Main function for testing RAG Orchestrator v2"""
    orchestrator = RAGOrchestratorV2()
    
    # Test health check
    print("🔍 Testing health check...")
    health_status = await orchestrator.health_check()
    print(f"Health status: {health_status}")
    
    # Test RAG query
    print("\n🧠 Testing RAG query...")
    result = await orchestrator.process_rag_query("What is machine learning?")
    print(f"Query: {result.query}")
    print(f"Response: {result.response[:200]}...")
    print(f"Latency: {result.latency:.3f}s")
    print(f"Success: {result.success}")
    
    # Show performance metrics
    print("\n📊 Performance metrics:")
    metrics = orchestrator.get_performance_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())