# Environment Variables

This document lists all the environment variables required for the Voice RAG Assistant.

## Required Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# ElevenLabs TTS Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id_here

# Google/Gemini LLM Configuration
GOOGLE_API_KEY=your_google_api_key_here
```

## Optional Environment Variables

These are for additional services that may be configured in the future:

```bash
# Deepgram STT (alternative to Whisper)
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# Cartesia TTS (alternative to ElevenLabs)
CARTESIA_API_KEY=your_cartesia_api_key_here

# Pinecone RAG (when replacing mock RAG)
PINECONE_API_KEY=your_pinecone_api_key_here
```

## Configuration Files

- `config.yaml` - Main configuration structure
- `config.py` - Configuration loader and environment variable substitution
- This file supports `${VAR_NAME}` syntax for environment variable substitution

## Fallback Values

If environment variables are not set, the system will use fallback values defined in the configuration. However, for security reasons, you should always set your own API keys in the environment variables. 