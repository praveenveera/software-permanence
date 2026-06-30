#!/usr/bin/env python3
import sys
import re

def verify_exports(file_path):
    """Parses a Python file to locate classes and functions."""
    exports = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # Matches top-level def and class declarations
                match = re.match(r"^(def|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
                if match:
                    exports.append((match.group(1), match.group(2)))
        return exports
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify_exports.py <file_path>")
        sys.exit(1)
    for typ, name in verify_exports(sys.argv[1]):
        print(f"[{typ.upper()}] {name}")
