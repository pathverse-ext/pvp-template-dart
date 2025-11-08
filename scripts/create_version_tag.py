#!/usr/bin/env python3
"""
Create and push version tag based on manifest.json
Runs on post-commit
"""

import json
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


def exec_command(command):
    """Execute a shell command and return output"""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    return result.stdout.strip(), result.returncode


def tag_exists(tag):
    """Check if a git tag exists"""
    _, returncode = exec_command(f'git rev-parse {tag}')
    return returncode == 0


def main():
    try:
        # Read manifest.json
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        if 'version' not in manifest:
            print('[!] No version found in manifest.json, skipping tag creation')
            return 0
        
        version = manifest['version']
        tag = f'v{version}'
        
        # Check if we're on main/master branch
        current_branch, _ = exec_command('git rev-parse --abbrev-ref HEAD')
        
        if current_branch not in ('main', 'master'):
            print(f'[INFO] Not on main/master branch ({current_branch}), skipping tag creation')
            return 0
        
        # Check if tag already exists
        if tag_exists(tag):
            print(f'[INFO] Tag {tag} already exists, skipping')
            return 0
        
        # Check if the current commit modified manifest.json or pubspec.yaml
        changed_files, _ = exec_command('git diff --name-only HEAD~1 HEAD')
        changed_files_list = changed_files.split('\n') if changed_files else []
        
        has_version_changes = any(
            f in ('manifest.json', 'pubspec.yaml')
            for f in changed_files_list
        )
        
        if not has_version_changes:
            print('[INFO] No version changes in this commit, skipping tag creation')
            return 0
        
        print(f'[*] Creating tag: {tag}')
        
        # Create annotated tag
        subprocess.run(
            ['git', 'tag', '-a', tag, '-m', f'Release version {version}'],
            check=True
        )
        
        print(f'[OK] Tag {tag} created successfully')
        
        # Push the tag to trigger the GitHub Action
        print(f'[*] Pushing tag {tag} to remote...')
        result = subprocess.run(
            ['git', 'push', 'origin', tag],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f'[OK] Tag {tag} pushed successfully')
            print('[INFO] GitHub Action will now build and create release')
        else:
            print(f'[!] Failed to push tag: {result.stderr}')
            print(f'    You can manually push with: git push origin {tag}')
        
        return 0
        
    except Exception as e:
        print(f'[ERROR] Error creating tag: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
