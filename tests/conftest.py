"""Lets tests import pipeline modules without SQL Server, pyodbc or a .env file."""
import os
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

os.environ.setdefault("DB_SERVER", "test-server")
os.environ.setdefault("DB_NAME", "test-db")

for name, attrs in (("pyodbc", {"connect": None}), ("dotenv", {"load_dotenv": lambda *a, **k: None})):
    try:
        __import__(name)
    except ImportError:
        module = types.ModuleType(name)
        for key, value in attrs.items():
            setattr(module, key, value)
        sys.modules[name] = module
