"""Pytest setup: make the repo root and the trading server importable."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

for _path in (REPO_ROOT, REPO_ROOT / 'trading-server'):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
