#!/usr/bin/env python3
"""
Ultra-Optimized RAG Orchestrator v2 Service Manager
Production deployment and management for ultra-fast RAG system
"""
import asyncio
import json
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Dict, Any
import subprocess
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from rag_orchestrator_v2_ultra_optimized import UltraOptimizedRAGOrchestratorV2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltraOptimizedServiceManager:
    """Service manager for ultra-optimized RAG Orchestrator v2"""
    
    def __init__(self):
        self.orchestrator = None
        self.running = False
        self.service_pid = None
        self.log_file = Path.home() / "ai" / "logs" / "ultra_optimized_service.log"
        self.pid_file = Path.home() / "ai" / "logs" / "ultra_optimized_service.pid"
        
    async def start_service(self):
        """Start the ultra-optimized RAG service"""
        try:
            logger.info("🚀 Starting Ultra-Optimized RAG Orchestrator v2 Service...")
            
            # Initialize orchestrator
            self.orchestrator = UltraOptimizedRAGOrchestratorV2()
            self.running = True
            
            # Perform initial health check
            health_status = await self.orchestrator.health_check()
            logger.info(f"Initial health check: {health_status}")
            
            # Start continuous operation
            await self.run_continuous()
            
        except Exception as e:
            logger.error(f"❌ Failed to start service: {e}")
            return False
    
    async def run_continuous(self):
        """Run the service continuously"""
        logger.info("🔄 Starting continuous operation...")
        
        try:
            while self.running:
                # Health check every 30 seconds
                health_status = await self.orchestrator.health_check()
                
                # Log performance metrics every 5 minutes
                if int(time.time()) % 300 == 0:
                    metrics = self.orchestrator.get_performance_metrics()
                    logger.info(f"Performance metrics: {metrics}")
                
                await asyncio.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("🛑 Service stopped by user")
        except Exception as e:
            logger.error(f"❌ Service error: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        self.running = False
        if self.orchestrator:
            await self.orchestrator.cleanup()
        logger.info("🧹 Service cleanup completed")
    
    def stop_service(self):
        """Stop the service"""
        logger.info("🛑 Stopping Ultra-Optimized RAG Orchestrator v2 Service...")
        self.running = False
        if self.service_pid:
            try:
                os.kill(self.service_pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        logger.info("✅ Service stopped")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status"""
        if not self.orchestrator:
            return {"status": "stopped", "message": "Service not running"}
        
        try:
            metrics = self.orchestrator.get_performance_metrics()
            return {
                "status": "running",
                "uptime_seconds": metrics["uptime_seconds"],
                "queries_processed": metrics["queries_processed"],
                "success_rate_percent": metrics["success_rate_percent"],
                "avg_response_time_s": metrics["avg_response_time_s"],
                "performance_grade": metrics["performance_grade"],
                "cache_stats": metrics["cache_stats"]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

class UltraOptimizedCLI:
    """CLI interface for managing ultra-optimized service"""
    
    def __init__(self):
        self.service_manager = UltraOptimizedServiceManager()
    
    async def start(self):
        """Start the service"""
        await self.service_manager.start_service()
    
    def stop(self):
        """Stop the service"""
        self.service_manager.stop_service()
    
    def status(self):
        """Show service status"""
        status = self.service_manager.get_service_status()
        print("🔍 Ultra-Optimized RAG Orchestrator v2 Service Status")
        print("=" * 60)
        
        if status["status"] == "running":
            print(f"✅ Status: {status['status'].upper()}")
            print(f"⏱️  Uptime: {status['uptime_seconds']:.1f} seconds")
            print(f"📊 Queries Processed: {status['queries_processed']}")
            print(f"✅ Success Rate: {status['success_rate_percent']:.1f}%")
            print(f"⚡ Avg Response Time: {status['avg_response_time_s']:.3f}s")
            print(f"🏆 Performance Grade: {status['performance_grade']}")
            print(f"💾 Cache Hit Rate: {status['cache_stats']['hit_rate_percent']:.1f}%")
        else:
            print(f"❌ Status: {status['status'].upper()}")
            print(f"📝 Message: {status['message']}")
    
    async def test(self):
        """Test the service with sample queries"""
        print("🧪 Testing Ultra-Optimized RAG Orchestrator v2...")
        print("=" * 60)
        
        try:
            orchestrator = UltraOptimizedRAGOrchestratorV2()
            
            # Test queries
            test_queries = [
                "What is machine learning?",
                "How does Docker work?",
                "Explain Python programming"
            ]
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n🔍 Test {i}: {query}")
                result = await orchestrator.process_rag_query_ultra_fast(query)
                
                print(f"   ⚡ Latency: {result.latency:.3f}s")
                print(f"   ✅ Success: {result.success}")
                print(f"   🤖 Model: {result.model_used}")
                print(f"   💾 Cache Hit: {result.cache_hit}")
                print(f"   📝 Response: {result.response[:100]}...")
            
            # Show final metrics
            print(f"\n📊 Final Performance Metrics:")
            metrics = orchestrator.get_performance_metrics()
            print(f"   Average Response Time: {metrics['avg_response_time_s']:.3f}s")
            print(f"   Success Rate: {metrics['success_rate_percent']:.1f}%")
            print(f"   Performance Grade: {metrics['performance_grade']}")
            
            await orchestrator.cleanup()
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    async def interactive(self):
        """Interactive query interface"""
        print("💬 Ultra-Optimized RAG Interactive Interface")
        print("=" * 60)
        print("Type your questions (or 'quit' to exit)")
        print()
        
        try:
            orchestrator = UltraOptimizedRAGOrchestratorV2()
            
            while True:
                query = input("🤔 Your question: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                print("⚡ Processing...")
                start_time = time.time()
                
                result = await orchestrator.process_rag_query_ultra_fast(query)
                
                print(f"\n🤖 Response ({result.latency:.3f}s):")
                print(f"   {result.response}")
                print(f"\n📊 Stats: Model={result.model_used}, Cache={result.cache_hit}, Success={result.success}")
                print()
            
            await orchestrator.cleanup()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main CLI function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ultra-Optimized RAG Orchestrator v2 Service Manager")
    parser.add_argument("command", choices=["start", "stop", "status", "test", "interactive"], 
                       help="Command to execute")
    
    args = parser.parse_args()
    cli = UltraOptimizedCLI()
    
    if args.command == "start":
        await cli.start()
    elif args.command == "stop":
        cli.stop()
    elif args.command == "status":
        cli.status()
    elif args.command == "test":
        await cli.test()
    elif args.command == "interactive":
        await cli.interactive()

if __name__ == "__main__":
    asyncio.run(main())