import os
import sys
import yaml
import re

def lint_context_file(file_path):
    print(f"--- Linting: {file_path} ---")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for YAML frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        print("[ERROR] Missing YAML frontmatter delimited by ---")
        return False

    try:
        header = yaml.safe_load(match.group(1))
    except Exception as e:
        print(f"[ERROR] Invalid YAML in frontmatter: {e}")
        return False

    # Required Header Fields
    required_fields = ['name', 'description', 'version', 'surgical_constants']
    for field in required_fields:
        if field not in header:
            print(f"[ERROR] Missing required field in frontmatter: {field}")
        else:
            print(f"[OK] Found field: {field}")

    # Check Verbosity (Body length)
    body = content[match.end():].strip()
    word_count = len(body.split())
    if word_count < 100:
        print(f"[WARNING] Context body is sparse ({word_count} words). Recommended > 100 words.")
    else:
        print(f"[OK] Verbosity: {word_count} words.")

    # Check for HEX Color codes
    hex_codes = re.findall(r'#[0-9A-Fa-f]{6}', content)
    if not hex_codes:
        print("[WARNING] No HEX color codes found. Visual DNA might be missing.")
    else:
        print(f"[OK] Found {len(hex_codes)} HEX color codes for visual consistency.")

    # Check for Surgical Constants in body
    if 'surgical_constants' in header:
        constants = header['surgical_constants']
        missing_constants = []
        for key, value in constants.items():
            if str(value).lower() not in body.lower():
                missing_constants.append(f"{key}:{value}")
        
        if missing_constants:
            print(f"[WARNING] Surgical constants mentioned in header but missing in body: {missing_constants}")
        else:
            print("[OK] All surgical constants reinforced in context body.")

    print("--- Linting Complete ---\n")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            lint_context_file(arg)
    else:
        # Default to linting the new registry
        registry_path = "context_registry/projects/daava"
        if os.path.exists(registry_path):
            for f in os.listdir(registry_path):
                if f.endswith(".agentmd") or f.endswith(".claudemd"):
                    lint_context_file(os.path.join(registry_path, f))
        else:
            print("Usage: python cdlc_linter.py <file_path>")
