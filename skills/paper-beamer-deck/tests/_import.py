"""Import the helper scripts by file path.

The scripts under ``../scripts/`` are standalone CLIs, not an importable package,
so the tests load them directly from disk. This keeps the tests hermetic and
working regardless of the current working directory.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from types import ModuleType

_SCRIPTS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, "scripts")
)


def load_script(name: str) -> ModuleType:
    """Load ``<scripts>/<name>.py`` as a module (without running its CLI)."""
    path = os.path.join(_SCRIPTS_DIR, f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    # Register before exec so @dataclass can resolve the module's namespace
    # (Python 3.14 looks the module up in sys.modules while processing fields).
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
