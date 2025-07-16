"""Core package for the Voice RAG Assistant.

This package contains the main VoiceAssistant class.
"""

try:
    # Try relative imports first (when running as module)
    from .voice_assistant import VoiceAssistant
except ImportError:
    # Fall back to absolute imports (when running as script)
    import sys
    from pathlib import Path

    # Add the parent directory to the path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from core.voice_assistant import VoiceAssistant

__all__ = [
    'VoiceAssistant',
]
