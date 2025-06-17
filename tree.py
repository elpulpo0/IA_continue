import os

EXCLUDE = {'.venv', '__pycache__', 'mlruns', '.git', '.pytest_cache'}

def print_tree(start_path='.', prefix=''):
    for entry in sorted(os.listdir(start_path)):
        if entry in EXCLUDE:
            continue
        path = os.path.join(start_path, entry)
        if os.path.isdir(path):
            print(f"{prefix}├── {entry}/")
            print_tree(path, prefix + "│   ")
        else:
            print(f"{prefix}├── {entry}")

print_tree()
