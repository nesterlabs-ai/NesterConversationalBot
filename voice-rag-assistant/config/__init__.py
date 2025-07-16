"""Configuration package for the Voice RAG Assistant.

This package contains configuration management functionality.
"""

try:
    # Try relative imports first (when running as module)
    from .config import load_config_from_yaml, get_assistant_config
except ImportError:
    # Fall back to absolute imports (when running as script)
    import sys
    from pathlib import Path

    # Add the parent directory to the path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from config.config import load_config_from_yaml, get_assistant_config

__all__ = [
    'load_config_from_yaml',
    'get_assistant_config',
]
