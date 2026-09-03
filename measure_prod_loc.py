import os

def count_prod_loc():
    root = os.path.dirname(os.path.abspath(__file__))
    exclude_dirs = {
        'tests', 'fixtures', 'node_modules', '.git', '__pycache__',
        '.pytest_cache', 'venv', '.venv', 'staticfiles', 'dist', 'build'
    }
    
    total_prod_lines = 0
    file_counts = {}
    language_counts = {'Python': 0, 'JavaScript': 0}
    oversized_files = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs and not d.startswith('.')]
        
        rel_dir = os.path.relpath(dirpath, root)
        if any(part in exclude_dirs for part in rel_dir.split(os.sep)):
            continue

        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in ('.py', '.js'):
                full_path = os.path.join(dirpath, f)
                size_kb = os.path.getsize(full_path) / 1024
                if size_kb > 1000:
                    oversized_files.append((full_path, size_kb))

                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                        lines = [line.strip() for line in fp if line.strip() and not line.strip().startswith('#')]
                        loc = len(lines)
                        total_prod_lines += loc
                        lang = 'Python' if ext == '.py' else 'JavaScript'
                        language_counts[lang] += loc
                        file_counts[os.path.relpath(full_path, root)] = (loc, size_kb)
                except Exception as e:
                    pass

    print("=" * 60)
    print("TrainPlex `measure-ext` Simulation: Production Source LOC")
    print("=" * 60)
    print(f"Total Production LOC: {total_prod_lines:,} (Required: 50,000+)")
    print(f"Python LOC:           {language_counts['Python']:,}")
    print(f"JavaScript LOC:       {language_counts['JavaScript']:,}")
    print(f"Total Prod Files:     {len(file_counts)}")
    print(f"Oversized (>1MB):     {len(oversized_files)}")
    print("=" * 60)
    if total_prod_lines >= 50000:
        print(">>> RESULT: PASS! Minimum 50,000+ prod LOC satisfied.")
    else:
        print(f">>> RESULT: FAIL! Need {50000 - total_prod_lines:,} more prod LOC.")
    print("=" * 60)

if __name__ == '__main__':
    count_prod_loc()
