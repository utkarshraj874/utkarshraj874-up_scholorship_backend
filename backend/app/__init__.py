import sys
from pathlib import Path

# Ensure project root (parent of backend) is in sys.path so 'backend.app' imports succeed from anywhere
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
