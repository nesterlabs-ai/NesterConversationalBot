"""Services package for the Voice RAG Assistant.

This package contains all the service classes that handle different
aspects of the voice assistant functionality.
"""

try:
    # Try relative imports first (when running as module)
    from .speech_to_text import SpeechToTextService
    from .text_to_speech import TextToSpeechService
    from .input_analyzer import InputAnalyzer
    from .rag_service import RAGService
    from .conversation_manager import ConversationManager
    from .latency_analyzer import LatencyAnalyzer
except ImportError:
    # Fall back to absolute imports (when running as script)
    import sys
    from pathlib import Path

    # Add the parent directory to the path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from services.speech_to_text import SpeechToTextService
    from services.text_to_speech import TextToSpeechService
    from services.input_analyzer import InputAnalyzer
    from services.rag_service import RAGService
    from services.conversation_manager import ConversationManager
    from services.latency_analyzer import LatencyAnalyzer

__all__ = [
    'SpeechToTextService',
    'TextToSpeechService',
    'InputAnalyzer',
    'RAGService',
    'ConversationManager',
    'LatencyAnalyzer',
]