"""Complete Voice Assistant server with FastAPI and WebSocket support.

This module provides both a FastAPI server with /connect endpoint and
WebSocket server functionality for the Voice Assistant.
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from config.config import get_assistant_config
from core.voice_assistant import VoiceAssistant
from voice_assistant_server import VoiceAssistantServer


# Global server instance
voice_assistant_server = VoiceAssistantServer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles FastAPI startup and shutdown."""
    yield  # Run app


# Initialize FastAPI app with lifespan manager
app = FastAPI(lifespan=lifespan)

# Configure CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """FastAPI WebSocket endpoint for Voice Assistant."""
    await websocket.accept()
    logger.info("Voice Assistant WebSocket connection accepted")
    
    try:
        # Create voice assistant for this connection
        voice_assistant = VoiceAssistant(voice_assistant_server.config)
        
        # Create a simple WebSocket wrapper that mimics the transport interface
        # This is a simplified approach - in production you might want to create
        # a proper FastAPI WebSocket transport adapter
        
        # For now, we'll create a basic handler
        logger.info("Voice Assistant WebSocket connection established")
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                message = await websocket.receive_text()
                logger.debug(f"Received message: {message}")
                
                # Here you would typically process the message through your voice assistant
                # This is a simplified example - you'd need to adapt this based on your
                # specific protocol and message format
                
            except Exception as e:
                logger.error(f"Error in WebSocket message handling: {e}")
                break
                
    except Exception as e:
        logger.error(f"Exception in Voice Assistant WebSocket endpoint: {e}")
    finally:
        logger.info("Voice Assistant WebSocket connection closed")


@app.post("/connect")
async def bot_connect(request: Request) -> Dict[Any, Any]:
    """Connect endpoint that returns the appropriate WebSocket URL."""
    server_mode = os.getenv("WEBSOCKET_SERVER", "fast_api")
    
    if server_mode == "websocket_server":
        # Return standalone WebSocket server URL
        host = voice_assistant_server.server_config.get("websocket_host", "localhost")
        port = voice_assistant_server.server_config.get("websocket_port", 8765)
        ws_url = f"ws://{host}:{port}"
    else:
        # Return FastAPI WebSocket endpoint URL
        host = voice_assistant_server.server_config.get("fastapi_host", "localhost")
        port = voice_assistant_server.server_config.get("fastapi_port", 7860)
        ws_url = f"ws://{host}:{port}/ws"
    
    logger.info(f"Returning WebSocket URL: {ws_url} (mode: {server_mode})")
    return {"ws_url": ws_url}


@app.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get the status of the voice assistant server."""
    return voice_assistant_server.get_server_status()


async def main():
    """Main function to run the appropriate server mode."""
    server_mode = os.getenv("WEBSOCKET_SERVER", "fast_api")
    
    # Load configuration
    config = load_config()
    voice_assistant_server.config = config
    
    tasks = []
    
    try:
        if server_mode == "websocket_server":
            logger.info("Starting in WebSocket server mode")
            tasks.append(voice_assistant_server.run_websocket_server())
        else:
            logger.info("Starting in FastAPI mode")
        
        # Always start the FastAPI server
        fastapi_config = uvicorn.Config(
            app, 
            host=config.get("server", {}).get("fastapi_host", "0.0.0.0"),
            port=config.get("server", {}).get("fastapi_port", 7860)
        )
        server = uvicorn.Server(fastapi_config)
        tasks.append(server.serve())
        
        # Run all tasks
        await asyncio.gather(*tasks)
        
    except asyncio.CancelledError:
        logger.info("Tasks cancelled (probably due to shutdown).")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


def load_config() -> Dict[str, Any]:
    """Load configuration from the existing config.py file."""
    return get_assistant_config()





if __name__ == "__main__":
    asyncio.run(main())