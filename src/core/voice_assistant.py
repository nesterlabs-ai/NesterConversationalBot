"""Main Voice Assistant orchestrator.

This module contains the main VoiceAssistant class that coordinates all services
and manages the overall voice assistant functionality.
"""

import asyncio
from typing import Dict, List, Any

from loguru import logger
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.transports.base_transport import BaseTransport

from src.services.conversation_manager import ConversationManager
from src.services.input_analyzer import InputAnalyzer
from src.services.latency_analyzer import LatencyAnalyzer
from src.services.rag_service import RAGService
from src.services.speech_to_text import SpeechToTextService
from src.services.text_to_speech import TextToSpeechService


class VoiceAssistant:
    """Main Voice Assistant class that coordinates all services.
    
    This class orchestrates the speech-to-text, text-to-speech, input analysis,
    RAG processing, and conversation management services to provide a complete
    voice assistant experience.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Voice Assistant.
        
        Args:
            config: Configuration dictionary containing settings for all services
        """
        self.config = config or {}

        # Initialize services
        self.stt_service = None
        self.tts_service = None
        self.input_analyzer = None
        self.rag_service = None
        self.conversation_manager = None

        # Pipeline components
        self.pipeline = None
        self.task = None
        self.runner = None
        self.rtvi = RTVIProcessor(config=RTVIConfig(config=[]))
        self.latency_analyzer = LatencyAnalyzer()

        logger.info("Initialized Voice Assistant")

    def initialize_services(self) -> None:
        """Initialize all the service components."""
        logger.info("Initializing Voice Assistant services...")

        # Initialize Speech-to-Text service
        stt_config = self.config.get("stt", {})
        self.stt_service = SpeechToTextService(
            stt_provider=stt_config.get("provider", "whisper"),
            **stt_config.get("config", {})
        )

        # Initialize Text-to-Speech service
        tts_config = self.config.get("tts", {})
        self.tts_service = TextToSpeechService(
            tts_provider=tts_config.get("provider", "elevenlabs"),
            **tts_config.get("config", {})
        )

        # Initialize Input Analyzer
        input_config = self.config.get("input_analyzer", {})
        self.input_analyzer = InputAnalyzer(
            custom_patterns=input_config.get("custom_patterns")
        )

        # Initialize RAG Service
        rag_config = self.config.get("rag", {})
        self.rag_service = RAGService(
            config=rag_config
        )

        # Initialize Conversation Manager
        conversation_config = self.config.get("conversation", {})
        language_config = self.config.get("language", {})
        self.conversation_manager = ConversationManager(
            input_analyzer=self.input_analyzer,
            rag_service=self.rag_service,
            llm_config=conversation_config.get("llm", {}),
            language_config=language_config
        )

        logger.info("All services initialized successfully")

    def create_pipeline(self, transport: BaseTransport) -> Pipeline:
        """Create the processing pipeline.
        
        Args:
            transport: The transport layer for audio input/output
            
        Returns:
            The configured pipeline
        """
        if not self.conversation_manager:
            raise ValueError("Services must be initialized before creating pipeline")

        # Get service instances
        stt = self.stt_service.get_service()
        tts = self.tts_service.get_service()
        llm = self.conversation_manager.get_llm_service()
        context_aggregator = self.conversation_manager.get_context_aggregator()

        # Set up TTS service in conversation manager for function call feedback
        self.conversation_manager.set_tts_service(tts)

        # Create pipeline
        self.pipeline = Pipeline([
            transport.input(),
            # self.latency_analyzer,  # Track latency metrics throughout pipeline
            stt,
            context_aggregator.user(),
            self.rtvi,
            llm,
            tts,
            transport.output(),
            context_aggregator.assistant(),
        ])

        logger.info("Pipeline created successfully")
        return self.pipeline

    def create_task(self, enable_metrics: bool = True) -> PipelineTask:
        """Create the pipeline task.
        
        Args:
            enable_metrics: Whether to enable metrics collection
            
        Returns:
            The configured pipeline task
        """
        if not self.pipeline:
            raise ValueError("Pipeline must be created before creating task")

        self.task = PipelineTask(
            self.pipeline,
            params=PipelineParams(
                enable_metrics=enable_metrics,
                enable_usage_metrics=enable_metrics,
            ),
            observers=[RTVIObserver(self.rtvi)],
        )

        logger.info("Pipeline task created successfully")
        return self.task

    def setup_transport_handlers(self, transport: BaseTransport) -> None:
        """Set up transport event handlers.
        
        Args:
            transport: The transport instance to set up handlers for
        """
        if not self.task:
            raise ValueError("Task must be created before setting up transport handlers")

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            logger.info(f"Client connected: {client}")
            # Kick off the conversation
            context_aggregator = self.conversation_manager.get_context_aggregator()
            await self.task.queue_frames([context_aggregator.user().get_context_frame()])
            logger.debug("Queued initial context frame")

        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            logger.info(f"Client disconnected: {client}")
            await self.task.cancel()
            logger.debug("Task cancelled due to client disconnect")

        logger.info("Transport handlers set up successfully")

    async def run(self, transport: BaseTransport, handle_sigint: bool = True) -> None:
        """Run the voice assistant.
        
        Args:
            transport: The transport layer for audio input/output
            handle_sigint: Whether to handle SIGINT for graceful shutdown
        """
        logger.info("Starting Voice Assistant...")

        # Initialize services if not already done
        if not self.conversation_manager:
            logger.debug("Initializing services...")
            self.initialize_services()
            logger.debug("Services initialized")

        # Create pipeline and task
        logger.debug("Creating pipeline...")
        self.create_pipeline(transport)
        logger.debug("Pipeline created")

        logger.debug("Creating task...")
        self.create_task()
        logger.debug("Task created")

        # Set up transport handlers
        logger.debug("Setting up transport handlers...")
        self.setup_transport_handlers(transport)
        logger.debug("Transport handlers set up")

        # Create and run the pipeline runner
        logger.info("Creating pipeline runner...")
        self.runner = PipelineRunner(handle_sigint=handle_sigint)
        logger.info("Starting pipeline runner...")
        await self.runner.run(self.task)

        logger.info("Voice Assistant stopped")

    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of all services.
        
        Returns:
            Dictionary containing the status of all services
        """
        return {
            "stt_service": {
                "initialized": self.stt_service is not None,
                "config": self.stt_service.get_config() if self.stt_service else None
            },
            "tts_service": {
                "initialized": self.tts_service is not None,
                "config": self.tts_service.get_config() if self.tts_service else None
            },
            "input_analyzer": {
                "initialized": self.input_analyzer is not None,
                "patterns": self.input_analyzer.get_patterns() if self.input_analyzer else None
            },
            "rag_service": {
                "initialized": self.rag_service is not None,
                "status": self.rag_service.get_status() if self.rag_service else None
            },
            "conversation_manager": {
                "initialized": self.conversation_manager is not None,
                "stats": self.conversation_manager.get_conversation_stats() if self.conversation_manager else None
            },
            "pipeline": {
                "created": self.pipeline is not None,
                "task_created": self.task is not None,
                "runner_created": self.runner is not None
            },
            "latency_analyzer": {
                "initialized": self.latency_analyzer is not None,
                "statistics": self.latency_analyzer.get_statistics() if self.latency_analyzer else None
            }
        }

    def update_service_config(self, service_name: str, config: Dict[str, Any]) -> None:
        """Update configuration for a specific service.
        
        Args:
            service_name: Name of the service to update
            config: New configuration parameters
        """
        if service_name == "stt" and self.stt_service:
            self.stt_service.update_config(**config)
        elif service_name == "tts" and self.tts_service:
            self.tts_service.update_config(**config)
        elif service_name == "rag" and self.rag_service:
            self.rag_service.update_config(config)
        else:
            logger.warning(f"Service {service_name} not found or not initialized")

    def get_latency_statistics(self) -> Dict[str, Any]:
        """Get current latency statistics.
        
        Returns:
            Dictionary containing latency statistics and metrics
        """
        if self.latency_analyzer:
            return self.latency_analyzer.get_statistics()
        return {"error": "Latency analyzer not initialized"}

    def reset_latency_statistics(self) -> None:
        """Reset all latency statistics."""
        if self.latency_analyzer:
            self.latency_analyzer.reset_statistics()
            logger.info("Latency statistics reset")
        else:
            logger.warning("Latency analyzer not initialized")

    def log_latency_report(self) -> None:
        """Log a comprehensive latency analysis report."""
        if self.latency_analyzer:
            self.latency_analyzer.log_summary_report()
        else:
            logger.warning("Latency analyzer not initialized")

    def get_recent_latency_metrics(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get metrics for the most recent interactions.
        
        Args:
            count: Number of recent interactions to return
            
        Returns:
            List of recent interaction metrics
        """
        if self.latency_analyzer:
            stats = self.latency_analyzer.get_statistics()
            return stats.get("recent_interactions", [])[-count:]
        return []

    def shutdown(self) -> None:
        """Gracefully shut down the voice assistant."""
        logger.info("Shutting down Voice Assistant...")

        if self.task:
            asyncio.create_task(self.task.cancel())

        logger.info("Voice Assistant shut down complete")

    @classmethod
    def create_from_config(cls, config_dict: Dict[str, Any]) -> "VoiceAssistant":
        """Create a VoiceAssistant instance from a configuration dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Configured VoiceAssistant instance
        """
        instance = cls(config_dict)
        instance.initialize_services()
        return instance
