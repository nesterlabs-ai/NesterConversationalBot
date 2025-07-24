"""Text-to-Speech service for the Voice RAG Assistant.

This module handles converting text responses to speech using various TTS engines.
"""

from typing import Any, Dict

from loguru import logger
from pipecat.frames.frames import TTSSpeakFrame
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService


class TextToSpeechService:
    """Service responsible for converting text to speech.
    
    This class encapsulates the text-to-speech functionality and provides
    a clean interface for speech synthesis.
    """

    def __init__(self, tts_provider: str = "elevenlabs", **kwargs):
        """Initialize the Text-to-Speech service.
        
        Args:
            tts_provider: The TTS provider to use ("elevenlabs" or "cartesia")
            **kwargs: Additional configuration parameters for the TTS service
        """
        self.tts_provider = tts_provider
        self.tts_service = None
        self.config = kwargs

    def initialize(self) -> Any:
        """Initialize the TTS service based on the provider.
        
        Returns:
            The initialized TTS service instance
        """
        if self.tts_provider == "elevenlabs":
            api_key = self.config.get("api_key")
            voice_id = self.config.get("voice_id")

            if not api_key:
                raise ValueError("ElevenLabs API key is required for elevenlabs provider")
            if not voice_id:
                raise ValueError("ElevenLabs voice ID is required for elevenlabs provider")

            # Select appropriate voice based on language
            language = self.config.get("language", "en")
            support_hinglish = self.config.get("support_hinglish", False)
            hinglish_voice_id = self.config.get("hinglish_voice_id")

            # Use Hinglish voice if supported and available
            if support_hinglish and hinglish_voice_id:
                selected_voice_id = hinglish_voice_id
                logger.info("Using Hinglish voice for TTS")
            else:
                selected_voice_id = voice_id
                logger.info(f"Using {language} voice for TTS")

            self.tts_service = ElevenLabsTTSService(
                api_key=api_key,
                voice_id=selected_voice_id,
                model="eleven_multilingual_v2"
            )
        elif self.tts_provider == "cartesia":
            api_key = self.config.get("api_key")
            voice_id = self.config.get("voice_id")

            if not api_key:
                raise ValueError("Cartesia API key is required for cartesia provider")
            if not voice_id:
                raise ValueError("Cartesia voice ID is required for cartesia provider")

            # Select appropriate voice based on language
            language = self.config.get("language", "en")
            support_hinglish = self.config.get("support_hinglish", False)
            hinglish_voice_id = self.config.get("hinglish_voice_id")

            # Use Hinglish voice if supported and available
            if support_hinglish and hinglish_voice_id:
                selected_voice_id = hinglish_voice_id
                logger.info("Using Hinglish voice for TTS")
            else:
                selected_voice_id = voice_id
                logger.info(f"Using {language} voice for TTS")

            self.tts_service = CartesiaTTSService(
                api_key=api_key,
                voice_id=selected_voice_id
            )
        else:
            raise ValueError(f"Unsupported TTS provider: {self.tts_provider}")

        logger.info(f"Initialized TTS service: {self.tts_provider}")
        return self.tts_service

    def get_service(self) -> Any:
        """Get the TTS service instance.
        
        Returns:
            The TTS service instance
        """
        if self.tts_service is None:
            self.initialize()
        return self.tts_service

    async def speak_text(self, text: str) -> None:
        """Convert text to speech and queue it for playback.
        
        Args:
            text: The text to convert to speech
        """
        if self.tts_service is None:
            self.initialize()

        try:
            await self.tts_service.queue_frame(TTSSpeakFrame(text))
            logger.info(f"Queued speech: {text[:50]}...")
        except Exception as e:
            logger.error(f"Failed to queue speech: {e}")
            raise

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration.
        
        Returns:
            Dictionary containing the current configuration
        """
        return {
            "provider": self.tts_provider,
            "config": self.config
        }

    def update_config(self, **kwargs) -> None:
        """Update the configuration.
        
        Args:
            **kwargs: New configuration parameters
        """
        self.config.update(kwargs)
        logger.info(f"Updated TTS config: {kwargs}")

        # Re-initialize if service was already created
        if self.tts_service is not None:
            logger.info("Re-initializing TTS service with new config")
            self.initialize()

    def get_voice_settings(self) -> Dict[str, Any]:
        """Get current voice settings.
        
        Returns:
            Dictionary containing voice settings
        """
        return {
            "provider": self.tts_provider,
            "voice_id": self.config.get("voice_id"),
            "api_key_configured": bool(self.config.get("api_key"))
        }
