"""Speech-to-Text service for the Voice RAG Assistant.

This module handles converting speech audio to text using various STT engines.
"""

import asyncio
from typing import Optional, Any, Dict
from loguru import logger

from pipecat.services.whisper.stt import WhisperSTTService
from pipecat.services.deepgram.stt import DeepgramSTTService


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
            self.stt_service = DeepgramSTTService(api_key=api_key)
        else:
            raise ValueError(f"Unsupported STT provider: {self.stt_provider}")
        
        logger.info(f"Initialized STT service: {self.stt_provider}")
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