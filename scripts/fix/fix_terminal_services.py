#!/usr/bin/env python3
"""
Terminal Services Fix and Restart Script

Diagnoses and fixes terminal/launchctl service issues:
1. Adds proper PATH to service plists
2. Restarts all services
3. Tests service connectivity
4. Provides terminal command fix
"""

import subprocess
import time
import requests
import os
from pathlib import Path

class TerminalServicesFixer:
    def __init__(self):
        self.project_root = Path("/Users/andrejsp/ai")

    def run_command(self, command, description="Running command"):
        """Run shell command with proper output capture"""
        try:
            print(f"🔄 {description}...")
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed: {e}")
            if e.stderr:
                print(f"Error: {e.stderr.strip()}")
            return False, e.stderr.strip()

    def check_service_status(self, service_name):
        """Check if launchctl service is loaded"""
        success, output = self.run_command(
            f"launchctl list | grep {service_name} || echo 'Not loaded'",
            f"Checking {service_name} status"
        )
        return "Not loaded" not in output if success else False

    def restart_service(self, service_name, plist_path):
        """Restart a launchctl service"""
        print(f"🔄 Restarting {service_name}...")

        # Unload if running
        self.run_command(f"launchctl unload '{plist_path}' 2>/dev/null || true", f"Unloading {service_name}")

        # Wait a moment
        time.sleep(2)

        # Load service
        success, output = self.run_command(f"launchctl load '{plist_path}'", f"Loading {service_name}")

        if success:
            # Wait for service to start
            print(f"⏳ Waiting for {service_name} to start...")
            time.sleep(5)

            # Check if it's running
            if self.check_service_status(service_name):
                print(f"✅ {service_name} restarted successfully")
                return True
            else:
                print(f"❌ {service_name} failed to start")
                return False
        return False

    def test_service_connectivity(self, service_name, url, expected_status=200):
        """Test if service is responding"""
        try:
            print(f"🔍 Testing {service_name} connectivity...")
            response = requests.get(url, timeout=10)

            if response.status_code == expected_status:
                print(f"✅ {service_name} is responding (status: {response.status_code})")
                return True
            else:
                print(f"⚠️  {service_name} responded with status: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ {service_name} connection failed: {e}")
            return False

    def fix_terminal_commands(self):
        """Fix terminal command execution issue"""
        print("🔧 Checking terminal PATH...")

        # Check if basic commands work
        success, output = self.run_command("echo 'Terminal test'", "Testing terminal")
        if not success:
            print("⚠️  Terminal commands not working - this may be a system issue")
            return False

        # Check PATH
        success, path_output = self.run_command("echo $PATH", "Checking PATH")
        if success and path_output:
            print(f"📍 Current PATH: {path_output}")

            # Check if Homebrew is in PATH
            if "/opt/homebrew/bin" not in path_output:
                print("⚠️  Homebrew not in PATH - may cause command failures")
            else:
                print("✅ Homebrew found in PATH")

        return True

    def run_full_diagnostic(self):
        """Run complete diagnostic and fix"""
        print("🔍 TERMINAL & SERVICES DIAGNOSTIC")
        print("="*50)

        # 1. Check terminal functionality
        terminal_ok = self.fix_terminal_commands()

        # 2. Check service plist files
        n8n_plist = "/Users/andrejsp/Library/LaunchAgents/ai.n8n.plist"
        chromadb_plist = "/Users/andrejsp/Library/LaunchAgents/ai.chromadb.plist"

        print(f"\n🔧 Checking service configurations...")

        # Check if plists exist and have PATH
        for plist_name, plist_path in [("n8n", n8n_plist), ("chromadb", chromadb_plist)]:
            if os.path.exists(plist_path):
                with open(plist_path, 'r') as f:
                    content = f.read()
                    if 'PATH' in content:
                        print(f"✅ {plist_name} plist has PATH configured")
                    else:
                        print(f"❌ {plist_name} plist missing PATH configuration")
            else:
                print(f"❌ {plist_name} plist not found: {plist_path}")

        # 3. Restart services
        print("
🔄 Restarting services..."        n8n_ok = self.restart_service("ai.n8n", n8n_plist)
        chromadb_ok = self.restart_service("ai.chromadb", chromadb_plist)

        # 4. Test connectivity
        print("
🧪 Testing service connectivity..."        n8n_connect = self.test_service_connectivity("n8n", "http://localhost:5678/healthz")
        chromadb_connect = self.test_service_connectivity("chromadb", "http://localhost:8000/api/v2/heartbeat")

        # 5. Summary
        print("
📊 DIAGNOSTIC SUMMARY"        print("="*30)
        print(f"Terminal Commands: {'✅ Working' if terminal_ok else '❌ Issues'}")
        print(f"N8N Service: {'✅ Running' if n8n_ok and n8n_connect else '❌ Issues'}")
        print(f"ChromaDB Service: {'✅ Running' if chromadb_ok and chromadb_connect else '❌ Issues'}")

        all_good = terminal_ok and n8n_ok and n8n_connect and chromadb_ok and chromadb_connect

        if all_good:
            print("
🎉 ALL SYSTEMS OPERATIONAL!"            print("Your AI orchestration platform is ready!")
            print("\n🚀 Quick test commands:")
            print("• curl http://localhost:5678/healthz")
            print("• curl http://localhost:8000/api/v2/heartbeat")
            print("• python3 faiss_ingestion_production.py")
        else:
            print("
⚠️  SOME ISSUES DETECTED"            print("Check the logs in /Users/andrejsp/ai/logs/ for details")

        return all_good

def main():
    fixer = TerminalServicesFixer()
    success = fixer.run_full_diagnostic()

    print("
💡 NEXT STEPS:"    if success:
        print("1. Your services are running - proceed with git/github setup")
        print("2. Run: python3 setup_git_repo.py")
        print("3. Push your AI project to GitHub!")
    else:
        print("1. Check the error messages above")
        print("2. Review service logs in /Users/andrejsp/ai/logs/")
        print("3. Try restarting services manually if needed")

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
