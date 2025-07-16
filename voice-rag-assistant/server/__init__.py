"""Server package for the Voice RAG Assistant.

This package contains server-related classes and FastAPI app.
"""

try:
    # Try relative imports first (when running as module)
    from .voice_assistant_server import VoiceAssistantServer
    from .websocket_server import app
except ImportError:
    # Fall back to absolute imports (when running as script)
    import sys
    from pathlib import Path
    
    # Add the parent directory to the path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from server.voice_assistant_server import VoiceAssistantServer
    from server.websocket_server import app

__all__ = [
    'VoiceAssistantServer',
    'app',
]
