# WebSocket Adapter for Voice RAG Assistant

This WebSocket adapter provides a simple way to connect any client to the Voice RAG Assistant using WebSocket connections. It uses the existing VoiceAssistant pipeline and pipecat framework without modifying the core services.

## Features

- **WebSocket Interface**: Real-time bidirectional communication
- **Session Management**: Each connection gets its own voice assistant instance
- **Existing Pipeline**: Uses the same STT/TTS/LLM flow as the original system
- **Audio Support**: Full audio input/output support via WebSocket
- **No Service Modifications**: Works with existing services without changes

## Setup

### 1. Environment Variables

Make sure you have your `.env` file configured:
```bash
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id
GOOGLE_API_KEY=your_google_api_key
```

### 2. Start the WebSocket Server

```bash
cd voice-rag-assistant
python websocket_adapter.py
```

The server will start on `http://localhost:8000`

## Usage

### WebSocket Connection

Connect to: `ws://localhost:8000/ws/{session_id}`

Replace `{session_id}` with any unique identifier for your session.

### Connection Flow

1. **Connect**: WebSocket connection is established
2. **Confirmation**: Server sends a connection confirmation message
3. **Audio Ready**: The voice assistant is ready to receive audio
4. **Conversation**: Send/receive audio through the WebSocket
5. **Cleanup**: Session is automatically cleaned up when disconnected

### Example Messages

#### Connection Confirmation
```json
{
  "type": "connection",
  "status": "connected",
  "session_id": "your_session_id",
  "message": "Voice Assistant ready"
}
```

## Testing

### Option 1: Python Client
```bash
python simple_client.py
```

### Option 2: HTML Client
Open `test_client.html` in your browser and:
1. Click "Connect"
2. Click "Start Audio" 
3. Speak to test the voice assistant
4. Click "Stop Audio" when done

### Option 3: Manual WebSocket Testing

Using a WebSocket client tool or browser console:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/test_session');

ws.onopen = function() {
    console.log('Connected to Voice Assistant');
};

ws.onmessage = function(event) {
    console.log('Received:', event.data);
};

// For audio input, send binary audio data directly
// The pipecat framework handles audio automatically
```

## How It Works

1. **WebSocket Connection**: Client connects to `/ws/{session_id}`
2. **Transport Creation**: Creates a `FastAPIWebsocketTransport` (same as Twilio example)
3. **Voice Assistant**: Initializes a new `VoiceAssistant` instance for the session
4. **Pipeline**: Runs the existing STT → Context → LLM → TTS pipeline
5. **Audio Handling**: Pipecat handles audio frames automatically
6. **Session Cleanup**: Cleans up resources when connection closes

## Architecture

```
Client (Browser/App)
     ↓ WebSocket
WebSocket Adapter
     ↓ FastAPIWebsocketTransport
Existing VoiceAssistant Pipeline
     ↓
STT → Input Analyzer → RAG → LLM → TTS
```

## API Endpoints

- `GET /` - Service status
- `GET /health` - Health check
- `WebSocket /ws/{session_id}` - Voice assistant connection

## Configuration

The WebSocket adapter uses the same configuration as the original system:
- `config.yaml` - Service configuration
- `.env` - Environment variables
- All existing service configurations are respected

## Session Management

- Each WebSocket connection creates a separate session
- Sessions are isolated (separate voice assistant instances)
- Automatic cleanup when connections close
- Session IDs can be any string (recommend UUIDs for uniqueness)

## Audio Requirements

- **Format**: Any format supported by the browser's MediaRecorder
- **Transmission**: Binary WebSocket messages
- **Processing**: Handled automatically by pipecat framework
- **Output**: Audio is sent back through the same WebSocket

## Limitations

- Each session uses memory for the voice assistant instance
- Audio processing is CPU-intensive (especially Whisper STT)
- No authentication (add as needed for production)
- CORS is open (configure for production)

## Production Considerations

1. **Authentication**: Add authentication for WebSocket connections
2. **Rate Limiting**: Implement rate limiting for connections and messages
3. **Monitoring**: Add metrics and logging for sessions
4. **Scaling**: Consider connection pooling for high volume
5. **Security**: Configure CORS and use WSS in production

## Troubleshooting

### Connection Issues
- Check that the server is running on port 8000
- Verify WebSocket URL format: `ws://localhost:8000/ws/session_id`
- Check browser console for WebSocket errors

### Audio Issues
- Ensure browser has microphone permissions
- Check that audio is being sent as binary data
- Verify environment variables are set correctly

### Service Issues
- Check server logs for errors
- Verify `config.yaml` and `.env` files are present
- Test with the simple Python client first

## Example Integration

```python
import asyncio
import websockets

async def voice_assistant_client():
    uri = "ws://localhost:8000/ws/my_session"
    
    async with websockets.connect(uri) as websocket:
        # Connection is ready
        print("Connected to Voice Assistant")
        
        # The WebSocket is now ready for audio communication
        # Use MediaRecorder in browser or audio libraries in Python
        # to send audio data through the WebSocket
        
        await websocket.recv()  # Listen for responses
```

This WebSocket adapter provides a clean, simple interface to the existing Voice RAG Assistant while maintaining all the original functionality and pipeline architecture. 