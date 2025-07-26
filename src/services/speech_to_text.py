"""Speech-to-Text service for the Voice RAG Assistant.

This module handles converting speech audio to text using various STT engines.
"""

from typing import Any, Dict

import unicodedata
from deepgram import LiveOptions
from loguru import logger
from pipecat.frames.frames import Frame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.whisper.stt import WhisperSTTService
from pipecat.transcriptions.language import Language


class TextNormalizedDeepgramSTTService(DeepgramSTTService):
    """Deepgram STT service that normalizes Unicode text to prevent JSON encoding issues."""

    def __init__(self, api_key: str, live_options: LiveOptions = None, **kwargs):
        super().__init__(api_key=api_key, live_options=live_options, **kwargs)

    def _normalize_text(self, text: str) -> str:
        """Normalize Unicode text to prevent JSON encoding issues."""
        if not text:
            return text

        try:
            # Normalize Unicode to NFC form (canonical decomposition, then canonical composition)
            normalized = unicodedata.normalize('NFC', text)
            # Ensure it's properly encoded as UTF-8
            return normalized.encode('utf-8').decode('utf-8')
        except (UnicodeError, TypeError) as e:
            logger.warning(f"Text normalization failed for '{text}': {e}")
            # Fallback: return original text
            return text

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        # Process the frame normally first
        await super().process_frame(frame, direction)

        # If this generated a transcription frame, intercept and normalize it
        if isinstance(frame, TranscriptionFrame) and frame.text:
            normalized_text = self._normalize_text(frame.text)
            if normalized_text != frame.text:
                logger.debug(f"Normalized text: '{frame.text}' -> '{normalized_text}'")
                # Create a new frame with normalized text
                normalized_frame = TranscriptionFrame(
                    text=normalized_text,
                    user_id=frame.user_id,
                    timestamp=frame.timestamp,
                    language=getattr(frame, 'language', None)
                )
                # Replace the original frame with normalized one
                await self.push_frame(normalized_frame, direction)
                return

        # For all other frames, push as normal
        await self.push_frame(frame, direction)


class SpeechToTextService:
    """Service responsible for converting speech to text.
    
    This class encapsulates the speech-to-text functionality and provides
    a clean interface for audio transcription.
    """

    def __init__(self, stt_provider: str = "whisper", **kwargs):
        """Initialize the Speech-to-Text service.
        
        Args:
            stt_provider: The STT provider to use ("whisper" or "deepgram")
            **kwargs: Additional configuration parameters for the STT service
        """
        self.stt_provider = stt_provider
        self.stt_service = None
        self.config = kwargs

    def initialize(self) -> Any:
        """Initialize the STT service based on the provider.
        
        Returns:
            The initialized STT service instance
        """
        if self.stt_provider == "whisper":
            self.stt_service = WhisperSTTService(
                device=self.config.get("device", "cpu"),
                model=self.config.get("model", "small"),
                no_speech_prob=self.config.get("no_speech_prob", 0.3)
            )
        elif self.stt_provider == "deepgram":
            api_key = self.config.get("api_key")
            if not api_key:
                raise ValueError("Deepgram API key is required for deepgram provider")

            # Language configuration for Deepgram
            language = self.config.get("language", "en")
            detect_language = self.config.get("detect_language", False)

            # Configure LiveOptions for Deepgram
            live_options_config = {
                "model": "nova-3"
            }
            if detect_language:
                live_options_config["detect_language"] = True
            else:
                if language == "hi" or self.config.get("support_hinglish", False):
                    live_options_config["language"] = "multi"
                else:
                    language_mapping = {
                        "en": Language.EN,
                        "hi": Language.HI
                    }
                    live_options_config["language"] = language_mapping.get(language, Language.EN)
            live_options = LiveOptions(**live_options_config)
            print(live_options)

            # Create normalized Deepgram STT service
            self.stt_service = TextNormalizedDeepgramSTTService(
                api_key=api_key,
                live_options=live_options
            )
        else:
            raise ValueError(f"Unsupported STT provider: {self.stt_provider}")

        language_info = self.config.get("language", "en")
        logger.info(f"Initialized STT service: {self.stt_provider} with language: {language_info}")
        return self.stt_service

    def get_service(self) -> Any:
        """Get the STT service instance.
        
        Returns:
            The STT service instance
        """
        if self.stt_service is None:
            self.initialize()
        return self.stt_service

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration.
        
        Returns:
            Dictionary containing the current configuration
        """
        return {
            "provider": self.stt_provider,
            "config": self.config
        }

    def update_config(self, **kwargs) -> None:
        """Update the configuration.
        
        Args:
            **kwargs: New configuration parameters
        """
        self.config.update(kwargs)
        logger.info(f"Updated STT config: {kwargs}")

        # Re-initialize if service was already created
        if self.stt_service is not None:
            logger.info("Re-initializing STT service with new config")
            self.initialize()
