import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
# prepend root scripts/shared to sys.path
shared = root / 'scripts' / 'shared'
sys.path.insert(0, str(shared))
from check_roles import main
if __name__ == '__main__':
    main()
