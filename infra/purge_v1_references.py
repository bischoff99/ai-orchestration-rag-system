#!/usr/bin/env python3
"""
Purge ChromaDB v1 API references from codebase
"""
import os
import re
from pathlib import Path

def find_v1_references():
    """Find all v1 API references in the codebase"""
    v1_patterns = [
        r'api/v2/',
        r'/v1/',
        r'v1/heartbeat',
        r'v1/version',
        r'v1/collections'
    ]
    
    ai_dir = Path("/Users/andrejsp/ai")
    v1_files = []
    
    print("🔍 Scanning for v1 API references...")
    
    for pattern in v1_patterns:
        for file_path in ai_dir.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(pattern, content):
                        v1_files.append((file_path, pattern))
                        print(f"   Found {pattern} in {file_path.relative_to(ai_dir)}")
            except Exception as e:
                continue
    
    return v1_files

def update_v1_references():
    """Update v1 references to v2"""
    print("\n🔄 Updating v1 references to v2...")
    
    replacements = {
        'api/v2/': 'api/v2/',
        '/v2/heartbeat': '/v2/heartbeat',
        '/v2/version': '/v2/version',
        '/v2/collections': '/v2/collections'
    }
    
    updated_files = []
    
    for file_path, pattern in find_v1_references():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            for old, new in replacements.items():
                content = content.replace(old, new)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_files.append(file_path)
                print(f"   ✅ Updated {file_path.relative_to(Path('/Users/andrejsp/ai'))}")
        
        except Exception as e:
            print(f"   ❌ Error updating {file_path}: {e}")
    
    return updated_files

def main():
    print("🧹 Purging ChromaDB v1 API References")
    print("=" * 50)
    
    # Find v1 references
    v1_files = find_v1_references()
    
    if not v1_files:
        print("✅ No v1 API references found!")
        return True
    
    print(f"\nFound {len(v1_files)} v1 references in {len(set(f[0] for f in v1_files))} files")
    
    # Update references
    updated_files = update_v1_references()
    
    if updated_files:
        print(f"\n✅ Updated {len(updated_files)} files")
        print("📋 Updated files:")
        for file_path in updated_files:
            print(f"   - {file_path.relative_to(Path('/Users/andrejsp/ai'))}")
    else:
        print("\n⚠️  No files were updated")
    
    # Verify no v1 references remain
    print("\n🔍 Verifying v1 references are purged...")
    remaining_v1 = find_v1_references()
    
    if not remaining_v1:
        print("✅ All v1 references successfully purged!")
        return True
    else:
        print(f"⚠️  {len(remaining_v1)} v1 references still remain")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)