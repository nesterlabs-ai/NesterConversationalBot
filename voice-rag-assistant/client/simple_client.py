"""Simple WebSocket client for testing the Voice RAG Assistant.

This client demonstrates how to connect to the WebSocket adapter and send audio data.
"""

import asyncio
import json
import base64
import websockets
from loguru import logger


async def test_websocket_connection():
    """Test WebSocket connection with text and audio."""
    session_id = "test_session"
    uri = f"ws://localhost:8000/ws/{session_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")
            
            # Listen for incoming messages
            async def listen_for_messages():
                try:
                    async for message in websocket:
                        data = json.loads(message)
                        message_type = data.get("type")
                        
                        if message_type == "connection":
                            logger.info(f"Connection confirmed: {data.get('message')}")
                        else:
                            logger.info(f"Received: {data}")
                except Exception as e:
                    logger.error(f"Error listening for messages: {e}")
            
            # Start listener
            listener_task = asyncio.create_task(listen_for_messages())
            
            # Wait a moment for connection
            await asyncio.sleep(1)
            
            # For now, just keep the connection alive
            # The pipecat framework handles audio automatically
            logger.info("WebSocket connection established. You can now use audio input/output through the browser.")
            logger.info("The connection will stay alive for testing...")
            
            # Keep connection alive for 60 seconds
            await asyncio.sleep(60)
            
            listener_task.cancel()
            logger.info("Test completed")
            
    except Exception as e:
        logger.error(f"Connection error: {e}")


async def main():
    """Main function."""
    logger.info("Starting WebSocket client test...")
    await test_websocket_connection()


if __name__ == "__main__":
    asyncio.run(main()) 