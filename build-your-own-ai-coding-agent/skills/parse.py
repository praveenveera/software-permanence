import sys, re

def parse_exports(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        exports = []
        for line in lines:
            # Match python functions and classes
            match = re.match(r"^(def|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
            if match:
                exports.append(f"{match.group(1)}: {match.group(2)}")
        
        print(f"File: {file_path}")
        print("Exports found:")
        for item in exports:
            print(f"  - {item}")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse.py <file_path>")
        sys.exit(1)
    parse_exports(sys.argv[1])
