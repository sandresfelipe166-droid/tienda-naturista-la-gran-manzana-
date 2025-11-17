"""
Scan repository for files with identical content and print groups of duplicates.
Useful to identify repeated files like fix_roles.py or redis binaries in multiple places.
Usage: python scripts/find_duplicates.py [path]
"""
import hashlib
import os
import sys
from collections import defaultdict

root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

hash_map = defaultdict(list)

SKIP_EXT = {'.exe', '.dll', '.so', '.png', '.jpg', '.jpeg', '.ico', '.zip', '.tar', '.gz', '.tgz', '.pdf'}
MAX_SIZE = 50 * 1024 * 1024  # 50 MB, skip huge binaries

for dirpath, dirs, files in os.walk(root):
    # skip virtualenvs, .git directories and node_modules
    if '.git' in dirs:
        dirs.remove('.git')
    if 'venv' in dirs:
        dirs.remove('venv')
    if '.venv' in dirs:
        dirs.remove('.venv')
    if 'node_modules' in dirs:
        dirs.remove('node_modules')

    for f in files:
        # skip common binary patterns that we don't want to fingerprint here
        full = os.path.join(dirpath, f)
        try:
            # skip heavy/binary files to avoid OOM or long reads
            if os.path.splitext(f)[1].lower() in SKIP_EXT:
                continue
            size = os.path.getsize(full)
            if size > MAX_SIZE:
                # skip very large files
                continue

            # read in chunks to avoid large memory spikes
            hasher = hashlib.sha256()
            with open(full, 'rb') as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    hasher.update(chunk)
            h = hasher.hexdigest()
            hash_map[(h, os.path.getsize(full))].append(full)
        except Exception:
            # unreadable or special files
            continue

# Print duplicates
for k, paths in hash_map.items():
    if len(paths) > 1:
        print("\n=== DUPLICATES (size, hash) ===")
        print(k)
        for p in paths:
            print(" -", p)

print('\nScan finished.')
