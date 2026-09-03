import os
import zipfile

def make_zip(output_filename='CineVerse_Movie_OTT_Streaming.zip'):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(root_dir, output_filename)
    
    ignore_dirs = {
        '.git', '__pycache__', '.pytest_cache', '.idea', '.vscode', 
        'venv', '.venv', 'env', 'node_modules'
    }
    ignore_extensions = {'.pyc', '.pyo', '.pyd'}

    print(f"Creating archive: {zip_path} ...")
    file_count = 0

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
            
            for file in files:
                if file == output_filename:
                    continue
                ext = os.path.splitext(file)[1].lower()
                if ext in ignore_extensions:
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_dir)
                
                zipf.write(full_path, rel_path)
                file_count += 1

    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"Successfully created {output_filename} ({size_mb:.2f} MB, {file_count} files included).")

if __name__ == '__main__':
    make_zip()
