from pathlib import Path
import sys

def ensure_app_importable():
    """Insert the correct subproject (backend/frontend) path into sys.path so 'app' can be imported.
    Prefer backend by default, but fallback to frontend. This allows shared scripts to be executed from repo root.
    """
    repo_root = Path(__file__).resolve().parents[2]
    for sub in ('inventario-backend', 'inventario-frontend'):
        candidate = repo_root / sub
        if (candidate / 'app').exists():
            sys.path.insert(0, str(candidate))
            return
    # if not found, do nothing - import will fail
