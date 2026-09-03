import os
import sys

EXTENSIONS = {'.py', '.html', '.css', '.js', '.sql', '.vtt', '.svg', '.json', '.yml', '.yaml', '.sh', '.conf', '.ini'}
EXCLUDE_DIRS = {'.git', '__pycache__', 'migrations', 'venv', '.venv', 'env', '.pytest_cache', 'staticfiles'}

def count_lines_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # Count non-empty lines
            meaningful = [l for l in lines if l.strip()]
            return len(lines), len(meaningful)
    except Exception:
        return 0, 0

def scan_project(root_dir='.'):
    total_lines = 0
    total_meaningful = 0
    by_category = {}
    by_extension = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        rel_dir = os.path.relpath(dirpath, root_dir)
        top_folder = rel_dir.split(os.sep)[0] if rel_dir != '.' else 'root'
        
        for file in filenames:
            ext = os.path.splitext(file)[1].lower()
            if ext in EXTENSIONS:
                filepath = os.path.join(dirpath, file)
                raw, meaningful = count_lines_in_file(filepath)
                total_lines += raw
                total_meaningful += meaningful
                
                by_category[top_folder] = by_category.get(top_folder, 0) + raw
                by_extension[ext] = by_extension.get(ext, 0) + raw

    print(f"==================================================")
    print(f"CineVerse Codebase Line Counter")
    print(f"Total Raw Lines:       {total_lines:,}")
    print(f"Total Meaningful Lines: {total_meaningful:,}")
    print(f"==================================================")
    print("Lines by Top Folder:")
    for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:25s}: {count:,}")
    print("--------------------------------------------------")
    print("Lines by Extension:")
    for ext, count in sorted(by_extension.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ext:10s}: {count:,}")
    print(f"==================================================")
    return total_lines, total_meaningful

if __name__ == '__main__':
    scan_project('.')
