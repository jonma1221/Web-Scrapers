import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def sanitize_test_name(name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_.\-]+", "_", name)
    return sanitized[:200]