"""
Tool to consolidate duplicate admin scripts from subprojects into root scripts/ with wrappers.
Run: python scripts/consolidate_scripts.py
automatically moves files and writes wrappers.
"""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
backend = root / 'inventario-backend'
frontend = root / 'inventario-frontend'
newscripts = root / 'scripts' / 'shared'
newscripts.mkdir(parents=True, exist_ok=True)

candidates = [
    'fix_roles.py', 'fix_roles_final.py', 'check_roles.py', 'setup_inventory_roles.py', 'setup_roles.py', 'seed_admin_user.py'
]

for name in candidates:
    b = backend / name
    f = frontend / name
    # prefer backend copy as source
    source = b if b.exists() else (f if f.exists() else None)
    if source:
        destination = newscripts / name
        shutil.copy2(source, destination)
        print('Copied', source, 'to', destination)
        # create wrapper in both locations
        for loc in (backend, frontend):
            wrapper = loc / name
            wrapper.write_text(f"import sys\nfrom pathlib import Path\nroot = Path(__file__).resolve().parents[1]\n# prepend root scripts/shared to sys.path\nshared = root / 'scripts' / 'shared'\nsys.path.insert(0, str(shared))\nfrom {name[:-3]} import main\nif __name__ == '__main__':\n    main()\n")
        print('Wrote wrappers for', name)
    else:
        print('Not found', name)
print('Done')
