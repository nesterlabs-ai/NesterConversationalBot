#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import argparse

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.network.fastapi_websocket import FastAPIWebsocketParams
from pipecat.transports.services.daily import DailyParams

from voice_assistant import VoiceAssistant

load_dotenv(override=True)
print("Loaded .env file")

from config import get_assistant_config



# We store functions so objects (e.g. SileroVADAnalyzer) don't get
# instantiated. The function will be called when the desired transport gets
# selected.
transport_params = {
    "daily": lambda: DailyParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_analyzer=SileroVADAnalyzer(),
    ),
    "twilio": lambda: FastAPIWebsocketParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_analyzer=SileroVADAnalyzer(),
    ),
    "webrtc": lambda: TransportParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_analyzer=SileroVADAnalyzer(),
    ),
}


async def run_server(transport: BaseTransport, _: argparse.Namespace, handle_sigint: bool):
    """Run the Voice Assistant example.
    
    Args:
        transport: The transport layer for audio input/output
        _: Command line arguments (unused)
        handle_sigint: Whether to handle SIGINT for graceful shutdown
    """
    logger.info("Starting Voice RAG Assistant")
    
    # Create assistant configuration
    config = get_assistant_config()
    
    # Create and run the Voice Assistant
    assistant = VoiceAssistant(config)
    
    try:
        await assistant.run(transport, handle_sigint)
    except Exception as e:
        logger.error(f"Error running voice assistant: {e}")
        raise
    finally:
        assistant.shutdown()


if __name__ == "__main__":
    from run import main

    main(run_server, transport_params=transport_params)