# ConversationalBot - Voice RAG Assistant

A real-time voice conversational assistant that combines speech-to-text, text-to-speech, RAG (Retrieval-Augmented Generation), and LLM capabilities for natural voice interactions.

## 🎯 Features

- **Real-time Voice Conversation**: WebSocket-based audio streaming with low latency
- **Speech-to-Text**: Supports Deepgram and Whisper for accurate transcription
- **Text-to-Speech**: ElevenLabs integration for natural voice synthesis
- **RAG Integration**: Knowledge retrieval system for context-aware responses
- **LLM Integration**: Google LLM for intelligent conversation management
- **Latency Monitoring**: Built-in performance analysis and metrics
- **Flexible Deployment**: FastAPI server or standalone WebSocket server modes
- **Web Client**: HTML-based test client for easy testing

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │  Python Client  │    │  Mobile Client  │
│   (HTML/JS)     │    │                 │    │   (Future)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                        ┌─────────────────┐
                        │  WebSocket API  │
                        │   (FastAPI)     │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │ Voice Assistant │
                        │  Orchestrator   │
                        └─────────────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────┐
    │                            │                            │
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│   STT   │    │   TTS   │    │   RAG   │    │   LLM   │    │ Latency │
│Service  │    │Service  │    │Service  │    │Manager  │    │Analyzer │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Required API keys:
  - Deepgram API key (for speech-to-text)
  - ElevenLabs API key (for text-to-speech)
  - Google API key (for LLM)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ConversationalBot
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
Copy the example file and configure your API keys:
```bash
cp env.example .env
```
Then edit `.env` with your actual API keys:
```bash
# Required API Keys
DEEPGRAM_API_KEY=your_deepgram_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id
GOOGLE_API_KEY=your_google_api_key

# Optional: Server Configuration (defaults provided)
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=7860
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=8765
```

4. **Run the server**:
```bash
# Option 1: FastAPI mode (recommended)
cd src
python websocket_server.py

# Option 2: Standalone WebSocket server
WEBSOCKET_SERVER=websocket_server python websocket_server.py
```

5. **Test the connection**:
Open `src/client/test_client.html` in your browser or run:
```bash
cd src/client
python simple_client.py
```

## 📁 Project Structure

```
ConversationalBot/
├── src/
│   ├── config/
│   │   ├── config.yaml          # Main configuration file
│   │   └── config.py            # Configuration management
│   ├── core/
│   │   └── voice_assistant.py   # Main orchestrator
│   ├── services/
│   │   ├── speech_to_text.py    # STT service
│   │   ├── text_to_speech.py    # TTS service
│   │   ├── rag_service.py       # RAG/knowledge service
│   │   ├── conversation_manager.py # LLM & conversation flow
│   │   ├── input_analyzer.py    # Input processing
│   │   └── latency_analyzer.py  # Performance monitoring
│   ├── client/
│   │   ├── test_client.html     # Web test client
│   │   └── simple_client.py     # Python test client
│   ├── websocket_server.py      # Main server application
│   └── voice_assistant_server.py # Server class
├── requirements.txt
├── env.example                  # Environment variables template
└── README.md
```

## ⚙️ Configuration

The system uses a YAML configuration file (`src/config/config.yaml`) with environment variable substitution:

```yaml
# Speech-to-Text Configuration
stt:
  provider: "deepgram"  # or "whisper"
  config:
    api_key: "${DEEPGRAM_API_KEY}"
    model: "small"
    no_speech_prob: 0.3

# Text-to-Speech Configuration
tts:
  provider: "elevenlabs"
  config:
    api_key: "${ELEVENLABS_API_KEY}"
    voice_id: "${ELEVENLABS_VOICE_ID}"

# LLM Configuration
conversation:
  llm:
    api_key: "${GOOGLE_API_KEY}"

# RAG Configuration
rag:
  type: "mock"  # Replace with your RAG system
  config: {}
```

## 🔧 Usage

### Web Client

1. Open `src/client/test_client.html` in your browser
2. Click "Connect" to establish WebSocket connection
3. Click "Start Audio" to begin voice interaction
4. Speak naturally - the system will respond with synthesized speech

### Python Client

```python
from src.core.voice_assistant import VoiceAssistant
from src.config.config import get_assistant_config

# Initialize with configuration
config = get_assistant_config()
assistant = VoiceAssistant(config)

# Create transport (WebSocket, etc.)
transport = create_your_transport()

# Run the assistant
await assistant.run(transport)
```

### API Endpoints

- **WebSocket**: `ws://localhost:7860/ws/{session_id}`
- **Connect**: `POST /connect` - Returns WebSocket URL
- **Status**: `GET /status` - Server and service status

## 🏃‍♂️ Server Modes

### FastAPI Mode (Default)
```bash
python websocket_server.py
```
- Provides both HTTP API and WebSocket endpoints
- Recommended for production use
- Includes CORS support and proper error handling

### Standalone WebSocket Mode
```bash
WEBSOCKET_SERVER=websocket_server python websocket_server.py
```
- Pure WebSocket server without HTTP overhead
- Better for dedicated voice applications
- Lower latency for real-time audio

## 🎛️ Services

### Speech-to-Text Service
- **Providers**: Deepgram, Whisper
- **Features**: Real-time transcription, noise suppression
- **Configuration**: Model selection, sensitivity settings

### Text-to-Speech Service
- **Providers**: ElevenLabs
- **Features**: Natural voice synthesis, voice cloning
- **Configuration**: Voice selection, audio quality

### RAG Service
- **Features**: Knowledge retrieval, context enhancement
- **Extensible**: Replace with your own RAG system
- **Current**: Mock implementation with sample knowledge

### Conversation Manager
- **Features**: Context management, conversation flow
- **LLM Integration**: Google LLM, OpenAI support
- **Function Calls**: Extensible tool integration

### Latency Analyzer
- **Metrics**: Processing time, response latency
- **Monitoring**: Real-time performance tracking
- **Reporting**: Statistical analysis and logging

## 🔧 Development

### Adding New Services

1. Create a service class in `src/services/`
2. Implement the required interface methods
3. Register the service in `VoiceAssistant`
4. Update configuration as needed

### Function Handlers and Service Integration

The system uses function handlers to enable the LLM to call specific functions and services. This allows for dynamic interaction between the conversation flow and backend services.

#### How Function Handlers Work

Function handlers are registered with the LLM service and can be called during conversation flow. The system currently supports:

1. **RAG System Integration**: Search knowledge base for specific information
2. **Service Function Calls**: Execute specific operations through the LLM
3. **Event Handlers**: Respond to function call lifecycle events

#### Registering Function Handlers

In your conversation manager, register function handlers during LLM initialization:

```python
def initialize_llm(self) -> LLMService:
    """Initialize the LLM service with function handlers."""
    # Initialize LLM service
    self.llm_service = GoogleLLMService(api_key=api_key)
    
    # Register function handlers
    self.llm_service.register_function("call_rag_system", self._handle_rag_call)
    self.llm_service.register_function("custom_function", self._handle_custom_function)
    
    return self.llm_service
```

#### Creating Custom Function Handlers

Function handlers must be async methods that accept `FunctionCallParams`:

```python
async def _handle_custom_function(self, params: FunctionCallParams) -> None:
    """Handle custom function calls from the LLM.
    
    Args:
        params: Function call parameters containing arguments and callback
    """
    # Extract arguments passed from LLM
    user_input = params.arguments.get("input", "")
    operation_type = params.arguments.get("type", "default")
    
    try:
        # Process the request
        result = await self.custom_service.process(user_input, operation_type)
        
        # Return result to LLM
        await params.result_callback(result)
    except Exception as e:
        logger.error(f"Error in custom function: {e}")
        error_response = f"Error processing request: {str(e)}"
        await params.result_callback(error_response)
```

#### Function Schema Definition

Define function schemas for the LLM to understand available functions:

```python
def create_function_schemas(self) -> ToolsSchema:
    """Create function schemas for LLM tool usage."""
    
    # RAG system function
    rag_function = FunctionSchema(
        name="call_rag_system",
        description="Search knowledge base for questions requiring specific information",
        properties={
            "question": {
                "type": "string",
                "description": "The user's question to search for",
            },
        },
        required=["question"],
    )
    
    # Custom function example
    custom_function = FunctionSchema(
        name="custom_function",
        description="Process user input with custom logic",
        properties={
            "input": {
                "type": "string",
                "description": "User input to process",
            },
            "type": {
                "type": "string",
                "description": "Type of processing to perform",
                "enum": ["analyze", "transform", "validate"]
            },
        },
        required=["input"],
    )
    
    return ToolsSchema(standard_tools=[rag_function, custom_function])
```

#### Event Handlers for Function Calls

Add event handlers to provide feedback during function execution:

```python
def set_tts_service(self, tts_service: Any) -> None:
    """Set up TTS service and function call event handlers."""
    self.tts_service = tts_service
    
    if self.llm_service:
        # Handler for when function calls start
        @self.llm_service.event_handler("on_function_calls_started")
        async def on_function_calls_started(service, function_calls):
            if self.tts_service:
                await self.tts_service.queue_frame(TTSSpeakFrame("Let me check on that."))
        
        # Handler for when function calls complete
        @self.llm_service.event_handler("on_function_calls_finished")
        async def on_function_calls_finished(service, function_calls):
            logger.info(f"Function calls completed: {function_calls}")
            # Optional: Provide completion feedback
            if self.tts_service:
                await self.tts_service.queue_frame(TTSSpeakFrame("Found the information."))
```

#### Complete Integration Example

Here's a complete example of integrating a new service with function handlers:

```python
class WeatherService:
    """Example weather service integration."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def get_weather(self, location: str) -> str:
        """Get weather information for a location."""
        # Your weather API integration here
        return f"Weather in {location}: Sunny, 22°C"

class ConversationManager:
    def __init__(self, weather_service: WeatherService):
        self.weather_service = weather_service
        # ... other initialization
    
    def initialize_llm(self) -> LLMService:
        """Initialize LLM with weather function handler."""
        self.llm_service = GoogleLLMService(api_key=api_key)
        
        # Register weather function handler
        self.llm_service.register_function("get_weather", self._handle_weather_call)
        
        return self.llm_service
    
    async def _handle_weather_call(self, params: FunctionCallParams) -> None:
        """Handle weather function calls."""
        location = params.arguments.get("location", "")
        
        try:
            weather_info = await self.weather_service.get_weather(location)
            await params.result_callback(weather_info)
        except Exception as e:
            error_msg = f"Unable to get weather for {location}: {str(e)}"
            await params.result_callback(error_msg)
    
    def create_function_schemas(self) -> ToolsSchema:
        """Include weather function in schemas."""
        weather_function = FunctionSchema(
            name="get_weather",
            description="Get current weather information for a location",
            properties={
                "location": {
                    "type": "string",
                    "description": "City or location name",
                },
            },
            required=["location"],
        )
        
        return ToolsSchema(standard_tools=[weather_function])
```

#### Best Practices for Function Handlers

1. **Error Handling**: Always wrap function logic in try-catch blocks
2. **Async Operations**: Use async/await for all function handlers
3. **Argument Validation**: Validate function arguments before processing
4. **Logging**: Log function calls for debugging and monitoring
5. **Timeouts**: Implement timeouts for long-running operations
6. **Response Format**: Return consistent, well-formatted responses

### Extending RAG Service

Replace the mock RAG service with your implementation:

```python
class CustomRAGService:
    def __init__(self, config):
        # Initialize your RAG system
        pass
    
    def get_response(self, query, context=None):
        # Your RAG logic here
        return response
```

### Custom LLM Integration

Add support for additional LLM providers:

```python
# In conversation_manager.py
def initialize_llm(self):
    provider = self.llm_config.get("provider", "google")
    if provider == "custom":
        return CustomLLMService(self.llm_config)
```

## 📊 Monitoring

### Latency Metrics
- Processing time per component
- End-to-end response time
- Real-time performance statistics

### Health Checks
- Service status monitoring
- Connection health
- Error tracking

### Logging
- Structured logging with Loguru
- Service-specific log levels
- Performance metrics logging

## 🐛 Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Check API keys in `.env` file (copy from `env.example` if needed)
   - Verify all required API keys are set and valid
   - Verify network connectivity
   - Ensure ports are available

2. **Audio Issues**:
   - Check microphone permissions
   - Verify audio format compatibility
   - Test with different browsers

3. **Performance Issues**:
   - Monitor latency analyzer output
   - Check system resources
   - Optimize pipeline configuration

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python websocket_server.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

- Built with [pipecat-ai](https://github.com/pipecat-ai/pipecat) framework
- Speech services powered by Deepgram and ElevenLabs
- LLM integration via Google AI

## 📞 Support

For questions and support:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the configuration documentation

---

**Note**: This is a development framework. For production use, implement proper security measures, error handling, and scalability considerations. 