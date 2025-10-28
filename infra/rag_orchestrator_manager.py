    #!/usr/bin/env python3
"""
RAG Orchestrator v2 Manager
Management interface for the RAG Orchestrator service
"""
import asyncio
import json
import requests
import time
from datetime import datetime
from pathlib import Path
import sys

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from rag_orchestrator_v2 import RAGOrchestratorV2

class RAGOrchestratorManager:
    """Management interface for RAG Orchestrator v2"""

    def __init__(self):
        self.orchestrator = None
        self.config_file = "/Users/andrejsp/ai/configs/rag_orchestrator_config.json"

    async def test_system(self):
        """Test the RAG system end-to-end"""
        print("🧪 Testing RAG Orchestrator v2 System")
        print("=" * 50)

        if not self.orchestrator:
            self.orchestrator = RAGOrchestratorV2()

        # Test health check
        print("1. Testing service health...")
        health_status = await self.orchestrator.health_check()
        for service, status in health_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {service}: {'Healthy' if status else 'Unhealthy'}")

        # Test RAG query
        print("\n2. Testing RAG query processing...")
        test_queries = [
            "What is machine learning?",
            "How does Docker work?",
            "Explain Python programming"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"   Query {i}: {query[:30]}...")
            result = await self.orchestrator.process_rag_query(query)

            if result.success:
                print(f"   ✅ Success ({result.latency:.3f}s) - {result.response[:50]}...")
            else:
                print(f"   ❌ Failed: {result.error}")

        # Show performance metrics
        print("\n3. Performance metrics:")
        metrics = self.orchestrator.get_performance_metrics()
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")

        return all(health_status.values())

    async def interactive_query(self):
        """Interactive query interface"""
        print("🤖 RAG Orchestrator v2 - Interactive Query Interface")
        print("Type 'quit' to exit, 'metrics' for performance data")
        print("=" * 60)

        if not self.orchestrator:
            self.orchestrator = RAGOrchestratorV2()

        while True:
            try:
                query = input("\n💬 Query: ").strip()

                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif query.lower() == 'metrics':
                    metrics = self.orchestrator.get_performance_metrics()
                    print("\n📊 Performance Metrics:")
                    for key, value in metrics.items():
                        if isinstance(value, float):
                            print(f"   {key}: {value:.3f}")
                        else:
                            print(f"   {key}: {value}")
                    continue
                elif not query:
                    continue

                print("🔄 Processing...")
                start_time = time.time()

                result = await self.orchestrator.process_rag_query(query)

                if result.success:
                    print(f"\n🤖 Response ({result.latency:.3f}s):")
                    print(f"   {result.response}")

                    if result.context:
                        print(f"\n📚 Context ({len(result.context)} sources):")
                        for i, ctx in enumerate(result.context[:2], 1):
                            print(f"   {i}. {ctx[:100]}...")
                else:
                    print(f"\n❌ Error: {result.error}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

    def show_status(self):
        """Show current service status"""
        print("📊 RAG Orchestrator v2 Status")
        print("=" * 40)

        # Check if service is running via launchctl
        import subprocess
        try:
            result = subprocess.run(['launchctl', 'list', 'ai.rag-orchestrator-v2'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Service: Running (launchctl)")
            else:
                print("❌ Service: Not running (launchctl)")
        except Exception as e:
            print(f"⚠️  Service: Unknown status ({e})")

        # Check log files
        log_dir = Path.home() / "ai" / "logs"
        if log_dir.exists():
            log_files = list(log_dir.glob("rag_orchestrator*"))
            if log_files:
                print(f"📁 Log files: {len(log_files)} found")
                for log_file in log_files:
                    size = log_file.stat().st_size
                    print(f"   - {log_file.name}: {size} bytes")
            else:
                print("📁 Log files: None found")
        else:
            print("📁 Log files: Directory not found")

    def install_service(self):
        """Install the launchctl service"""
        print("🔧 Installing RAG Orchestrator v2 Service...")

        try:
            # Copy plist to LaunchAgents
            plist_src = "/Users/andrejsp/ai/infra/launchctl/rag_orchestrator_v2.plist"
            plist_dst = Path.home() / "Library" / "LaunchAgents" / "ai.rag-orchestrator-v2.plist"

            import shutil
            shutil.copy2(plist_src, plist_dst)
            print(f"✅ Plist copied to {plist_dst}")

            # Load the service
            import subprocess
            result = subprocess.run(['launchctl', 'load', str(plist_dst)],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Service loaded successfully")
            else:
                print(f"❌ Failed to load service: {result.stderr}")

        except Exception as e:
            print(f"❌ Installation failed: {e}")

    def uninstall_service(self):
        """Uninstall the launchctl service"""
        print("🗑️  Uninstalling RAG Orchestrator v2 Service...")

        try:
            plist_path = Path.home() / "Library" / "LaunchAgents" / "ai.rag-orchestrator-v2.plist"

            # Unload the service
            import subprocess
            result = subprocess.run(['launchctl', 'unload', str(plist_path)],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Service unloaded successfully")
            else:
                print(f"⚠️  Service unload warning: {result.stderr}")

            # Remove plist file
            if plist_path.exists():
                plist_path.unlink()
                print("✅ Plist file removed")

        except Exception as e:
            print(f"❌ Uninstallation failed: {e}")

async def main():
    """Main management interface"""
    manager = RAGOrchestratorManager()

    if len(sys.argv) < 2:
        print("RAG Orchestrator v2 Manager")
        print("Usage:")
        print("  python3 rag_orchestrator_manager.py test        - Test the system")
        print("  python3 rag_orchestrator_manager.py query       - Interactive query")
        print("  python3 rag_orchestrator_manager.py status      - Show status")
        print("  python3 rag_orchestrator_manager.py install     - Install service")
        print("  python3 rag_orchestrator_manager.py uninstall   - Uninstall service")
        return

    command = sys.argv[1].lower()

    if command == "test":
        success = await manager.test_system()
        sys.exit(0 if success else 1)
    elif command == "query":
        await manager.interactive_query()
    elif command == "status":
        manager.show_status()
    elif command == "install":
        manager.install_service()
    elif command == "uninstall":
        manager.uninstall_service()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())
