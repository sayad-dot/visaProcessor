#!/usr/bin/env python3
"""
Script to find and update all Gemini model references in the project.
"""
import os
import re
import argparse
from pathlib import Path

def find_and_replace_gemini_models(root_dir, dry_run=True):
    """Find all Gemini model references and optionally replace them."""
    
    # Patterns to search for (case-insensitive)
    patterns = [
        r'gemini-\d\.\d-(flash|pro)',  # models/gemini-2.5-flash, models/gemini-2.5-flash, etc.
        r'gemini-\d\.\d-flash-exp',    # models/gemini-2.5-flash-exp
        r'gemini-\d\.\d-pro-latest',   # models/gemini-2.5-flash-latest
        r'models/gemini-2.5-flash',
        r'models/gemini-2.5-flash',
        r'gemini-\d\.\d-flash-\d+',    # models/gemini-2.5-flash-001
        r'gemini-\d\.\d-pro-\d+',      # models/gemini-2.5-flash-001
    ]
    
    # Combine patterns
    pattern = re.compile('|'.join(patterns), re.IGNORECASE)
    
    # Files to exclude
    exclude_dirs = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', 'build', 'dist'}
    exclude_files = {__file__, 'test_gemini.py', 'test_gemini2.py', 'test_final.py', 'test_pro_model.py'}
    
    # New model to use
    new_model = 'models/models/gemini-2.5-flash'
    
    found_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                
                # Skip excluded files
                if file_path.absolute() in exclude_files:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find all matches
                    matches = pattern.findall(content)
                    if matches:
                        # Clean up matches (findall returns tuples when there are groups)
                        clean_matches = []
                        for match in matches:
                            if isinstance(match, tuple):
                                # Join tuple elements and filter out empty strings
                                clean_match = ''.join([m for m in match if m])
                                if clean_match:
                                    clean_matches.append(clean_match)
                            else:
                                clean_matches.append(match)
                        
                        if clean_matches:
                            found_files.append((file_path, clean_matches))
                            
                            if not dry_run:
                                # Replace all occurrences
                                new_content = pattern.sub(new_model, content)
                                
                                # Also handle models with "models/" prefix already
                                # Replace any occurrence that starts with models/ but contains old pattern
                                models_pattern = re.compile(r'models/' + '|'.join(patterns), re.IGNORECASE)
                                new_content = models_pattern.sub(new_model, new_content)
                                
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                
                except Exception as e:
                    print(f"⚠️ Error processing {file_path}: {e}")
    
    return found_files

def print_summary(found_files, dry_run):
    """Print summary of found files and changes."""
    print(f"\n{'='*60}")
    print(f"{'DRY RUN' if dry_run else 'ACTUAL UPDATE'}")
    print(f"{'='*60}\n")
    
    if not found_files:
        print("❌ No Gemini model references found.")
        return
    
    print(f"✅ Found {len(found_files)} files with Gemini model references:\n")
    
    for file_path, matches in found_files:
        print(f"📄 {file_path}")
        print(f"   Found: {', '.join(set(matches))}")
        print()

def main():
    parser = argparse.ArgumentParser(description='Update Gemini model references in project')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--path', default='.', help='Path to project root (default: current directory)')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry run)')
    
    args = parser.parse_args()
    
    # Determine if dry run
    dry_run = not args.apply if args.apply else args.dry_run
    
    print(f"🔍 Searching for Gemini model references in: {args.path}")
    print(f"📝 Mode: {'Dry Run (no changes)' if dry_run else 'Applying Changes'}")
    print(f"🎯 New model: models/models/gemini-2.5-flash\n")
    
    found_files = find_and_replace_gemini_models(args.path, dry_run)
    print_summary(found_files, dry_run)
    
    if dry_run and found_files:
        print("\n💡 To apply changes, run:")
        print(f"   python {__file__} --apply --path {args.path}")
    
    # Also check config.py specifically
    config_path = Path(args.path) / 'app' / 'config.py'
    if config_path.exists():
        print(f"\n{'='*60}")
        print("Checking config.py for GEMINI_MODEL setting...")
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Look for GEMINI_MODEL setting
            gemini_model_match = re.search(r'GEMINI_MODEL:\s*str\s*=\s*["\']([^"\']+)["\']', content)
            if gemini_model_match:
                current_model = gemini_model_match.group(1)
                print(f"📋 Current GEMINI_MODEL in config.py: {current_model}")
                
                if 'models/models/gemini-2.5-flash' not in current_model:
                    print(f"🔄 Should be updated to: models/models/gemini-2.5-flash")
                    if not dry_run:
                        new_content = re.sub(
                            r'(GEMINI_MODEL:\s*str\s*=\s*["\'])[^"\']+(["\'])',
                            r'\1models/models/gemini-2.5-flash\2',
                            content
                        )
                        with open(config_path, 'w') as f:
                            f.write(new_content)
                        print("✅ Updated config.py")
                else:
                    print("✅ Already set to models/models/gemini-2.5-flash")
        except Exception as e:
            print(f"⚠️ Error checking config.py: {e}")

if __name__ == '__main__':
    main()