#!/usr/bin/env python3
"""
Sync version from manifest.json to pubspec.yaml
Runs on pre-commit when manifest.json is modified
"""

import json
import re
import sys
import subprocess
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Get repository root
REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = REPO_ROOT / "manifest.json"
PUBSPEC_PATH = REPO_ROOT / "pubspec.yaml"


def main():
    try:
        # Read manifest.json
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        if 'version' not in manifest:
            print('[!] No version found in manifest.json')
            return 0
        
        manifest_version = manifest['version']
        print(f'[*] Manifest version: {manifest_version}')
        
        # Read pubspec.yaml
        with open(PUBSPEC_PATH, 'r', encoding='utf-8') as f:
            pubspec_content = f.read()
        
        # Extract current version from pubspec.yaml
        version_match = re.search(r'^version:\s*(.+)$', pubspec_content, re.MULTILINE)
        
        if not version_match:
            print('[!] No version found in pubspec.yaml')
            return 0
        
        current_version = version_match.group(1).strip()
        
        if current_version == manifest_version:
            print('[OK] Versions already in sync')
            return 0
        
        print(f'[*] Syncing version: {current_version} -> {manifest_version}')
        
        # Update pubspec.yaml version
        pubspec_content = re.sub(
            r'^version:\s*.+$',
            f'version: {manifest_version}',
            pubspec_content,
            flags=re.MULTILINE
        )
        
        with open(PUBSPEC_PATH, 'w', encoding='utf-8') as f:
            f.write(pubspec_content)
        
        # Stage the updated pubspec.yaml
        subprocess.run(['git', 'add', 'pubspec.yaml'], check=True)
        
        print('[OK] pubspec.yaml updated and staged')
        return 0
        
    except Exception as e:
        print(f'[ERROR] Error syncing version: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
