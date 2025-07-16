"""Voice Assistant Server class for handling WebSocket connections."""

import os
from typing import Dict, Any

from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.serializers.protobuf import ProtobufFrameSerializer
from pipecat.transports.network.websocket_server import (
    WebsocketServerParams,
    WebsocketServerTransport,
)

from core.voice_assistant import VoiceAssistant


class VoiceAssistantServer:
    """Complete Voice Assistant server with FastAPI and WebSocket support."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Voice Assistant server.
        
        Args:
            config: Configuration dictionary for the voice assistant and server
        """
        self.config = config or {}
        # Get server config with default values if not present
        self.server_config = self.config.get("server", {})
        self._apply_server_defaults()
        self.voice_assistant = None
        self.websocket_server_transport = None

        logger.info("Initialized Voice Assistant Server")

    def _apply_server_defaults(self):
        """Apply default server configuration values."""
        defaults = {
            "fastapi_host": os.getenv("FASTAPI_HOST", "0.0.0.0"),
            "fastapi_port": int(os.getenv("FASTAPI_PORT", "7860")),
            "websocket_host": os.getenv("WEBSOCKET_HOST", "localhost"),
            "websocket_port": int(os.getenv("WEBSOCKET_PORT", "8765")),
            "session_timeout": int(os.getenv("SESSION_TIMEOUT", "180")),
            "audio_in_enabled": os.getenv("AUDIO_IN_ENABLED", "true").lower() == "true",
            "audio_out_enabled": os.getenv("AUDIO_OUT_ENABLED", "true").lower() == "true",
            "add_wav_header": os.getenv("ADD_WAV_HEADER", "false").lower() == "true",
            "vad": {}
        }

        # Apply defaults for missing keys
        for key, value in defaults.items():
            if key not in self.server_config:
                self.server_config[key] = value

    def create_websocket_transport(self) -> WebsocketServerTransport:
        """Create and configure the standalone WebSocket transport.
        
        Returns:
            Configured WebSocket transport for standalone server
        """
        # Get server configuration with defaults
        host = self.server_config.get("websocket_host", "localhost")
        port = self.server_config.get("websocket_port", 8765)
        session_timeout = self.server_config.get("session_timeout", 60 * 3)  # 3 minutes
        audio_in_enabled = self.server_config.get("audio_in_enabled", True)
        audio_out_enabled = self.server_config.get("audio_out_enabled", True)
        add_wav_header = self.server_config.get("add_wav_header", False)

        # Create VAD analyzer (enabled by default)
        vad_config = self.server_config.get("vad", {})
        vad_analyzer = SileroVADAnalyzer(**vad_config)

        # Create transport parameters
        transport_params = WebsocketServerParams(
            host=host,
            port=port,
            serializer=ProtobufFrameSerializer(),
            audio_in_enabled=audio_in_enabled,
            audio_out_enabled=audio_out_enabled,
            add_wav_header=add_wav_header,
            vad_analyzer=vad_analyzer,
            session_timeout=session_timeout,
        )

        self.websocket_server_transport = WebsocketServerTransport(params=transport_params)

        logger.info(f"Created standalone WebSocket transport on {host}:{port}")
        return self.websocket_server_transport

    async def run_websocket_server(self) -> None:
        """Run the standalone WebSocket server."""
        logger.info("Starting standalone Voice Assistant WebSocket Server...")

        try:
            # Create voice assistant
            voice_assistant = VoiceAssistant(self.config)

            # Create transport
            transport = self.create_websocket_transport()

            # Set up transport handlers
            self.setup_websocket_transport_handlers(transport, voice_assistant)

            # Run the voice assistant with the transport
            await voice_assistant.run(transport, handle_sigint=False)

        except Exception as e:
            logger.error(f"Error running standalone WebSocket Server: {e}")
            raise

    def setup_websocket_transport_handlers(self, transport: WebsocketServerTransport,
                                           voice_assistant: VoiceAssistant) -> None:
        """Set up transport event handlers for standalone WebSocket server."""

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            logger.info(f"Voice Assistant client connected: {client.remote_address}")

        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            logger.info(f"Voice Assistant client disconnected: {client.remote_address}")

        @transport.event_handler("on_session_timeout")
        async def on_session_timeout(transport, client):
            logger.info(f"Session timeout for client: {client.remote_address}")

    def get_server_status(self) -> Dict[str, Any]:
        """Get the status of the server and voice assistant."""
        status = {
            "server": {
                "mode": os.getenv("WEBSOCKET_SERVER", "fast_api"),
                "config": self.server_config
            }
        }

        if hasattr(self, 'voice_assistant') and self.voice_assistant:
            if hasattr(self.voice_assistant, 'get_service_status'):
                status["voice_assistant"] = self.voice_assistant.get_service_status()

        return status
