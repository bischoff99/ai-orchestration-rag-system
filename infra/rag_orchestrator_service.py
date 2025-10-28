#!/usr/bin/env python3
"""
RAG Orchestrator v2 Service Manager
Production service management for the RAG Orchestrator
"""
import asyncio
import json
import signal
import sys
import time
from pathlib import Path
from datetime import datetime
import logging

# Add the parent directory to the path to import the orchestrator
sys.path.append(str(Path(__file__).parent.parent))

from rag_orchestrator_v2 import RAGOrchestratorV2

class RAGOrchestratorService:
    """Service manager for RAG Orchestrator v2"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "/Users/andrejsp/ai/configs/rag_orchestrator_config.json"
        self.orchestrator = None
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """Setup service logging"""
        log_dir = Path.home() / "ai" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "rag_orchestrator_service.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("RAGOrchestratorService")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop()
        sys.exit(0)
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            self.logger.info(f"Configuration loaded from {self.config_file}")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return None
    
    async def start(self):
        """Start the RAG Orchestrator service"""
        self.logger.info("Starting RAG Orchestrator v2 Service...")
        
        # Load configuration
        config = self.load_config()
        if not config:
            self.logger.error("Failed to load configuration, exiting")
            return
        
        # Initialize orchestrator
        self.orchestrator = RAGOrchestratorV2()
        self.running = True
        
        # Start the orchestrator
        try:
            await self.orchestrator.start()
        except Exception as e:
            self.logger.error(f"Orchestrator error: {e}")
        finally:
            self.running = False
            self.logger.info("RAG Orchestrator v2 Service stopped")
    
    def stop(self):
        """Stop the RAG Orchestrator service"""
        self.logger.info("Stopping RAG Orchestrator v2 Service...")
        self.running = False
        if self.orchestrator:
            self.orchestrator.stop()

async def main():
    """Main function for the service"""
    service = RAGOrchestratorService()
    
    try:
        await service.start()
    except KeyboardInterrupt:
        service.logger.info("Service interrupted by user")
    except Exception as e:
        service.logger.error(f"Service error: {e}")
    finally:
        service.stop()

if __name__ == "__main__":
    asyncio.run(main())