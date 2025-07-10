# Latency Analysis Documentation

The Voice Assistant now includes comprehensive latency analysis to help you monitor and optimize performance for each user query and response.

## Features

### 🔍 **Automatic Latency Tracking**
- Tracks timing for every voice interaction
- Measures individual component latencies (STT, LLM, TTS)
- Calculates voice-to-voice latency (most important metric)
- Assigns unique ID to each interaction for tracking

### 📊 **Key Metrics**

| Metric | Description | Good Target | Excellent Target |
|--------|-------------|-------------|------------------|
| **Voice-to-Voice** | User stops speaking → Bot starts speaking | < 1200ms | < 800ms |
| **STT Latency** | Speech-to-text processing time | < 500ms | < 300ms |
| **LLM Latency** | Language model response generation | < 1000ms | < 500ms |
| **TTS Latency** | Text-to-speech conversion time | < 400ms | < 200ms |
| **Total Latency** | Complete interaction processing time | < 2000ms | < 1500ms |

### 📈 **Statistics Tracking**
- Average, minimum, and maximum latencies
- 95th and 99th percentile calculations
- Real-time performance monitoring
- Historical interaction data

## Usage

### Basic Usage

```python
from voice_assistant import VoiceAssistant

# Latency analysis is automatically enabled
assistant = VoiceAssistant(config)

# Get current statistics
stats = assistant.get_latency_statistics()
print(f"Average voice-to-voice latency: {stats['current_stats']['average_latencies']['voice_to_voice_latency']:.2f}ms")

# Get recent interaction metrics
recent_metrics = assistant.get_recent_latency_metrics(count=5)
for metric in recent_metrics:
    print(f"Interaction {metric['interaction_id']}: {metric['voice_to_voice_latency_ms']:.2f}ms")
```

### Advanced Usage

```python
# Generate comprehensive report
assistant.log_latency_report()

# Reset statistics (useful for testing)
assistant.reset_latency_statistics()

# Monitor service status
service_status = assistant.get_service_status()
latency_stats = service_status['latency_analyzer']['statistics']
```

## Automatic Features

### 🔄 **Periodic Reporting**
- Automatic latency reports every 5 minutes
- Final report when assistant shuts down
- Structured logging for external analysis

### 📋 **Log Output Examples**

**Per-Interaction Logging:**
```
🔍 Latency Analysis - Interaction interaction_1_1704067200000
  📊 Voice-to-Voice: 721.25ms
  🎤 Speech-to-Text: 150.25ms
  🧠 LLM Processing: 450.75ms
  🔊 Text-to-Speech: 120.50ms
  ⏱️ Total Latency: 850.00ms
```

**Summary Report:**
```
============================================================
📊 LATENCY ANALYSIS SUMMARY REPORT
============================================================
Total Interactions: 25

📈 Average Latencies:
  Stt Latency: 165.43ms
  Llm Latency: 523.21ms
  Tts Latency: 145.67ms
  Total Latency: 1234.56ms
  Voice To Voice Latency: 834.31ms

📊 Performance Ranges:
  Voice To Voice Latency: 645.12ms - 1456.78ms
  Stt Latency: 89.23ms - 289.45ms
  Llm Latency: 234.56ms - 876.54ms
  Tts Latency: 78.90ms - 234.56ms

📊 95th Percentile Latencies:
  Voice To Voice Latency: 1123.45ms
  Stt Latency: 245.67ms
  Llm Latency: 789.12ms
  Tts Latency: 198.34ms
============================================================
```

## Integration in Pipeline

The latency analyzer is positioned early in the pipeline to capture all frame timings:

```python
self.pipeline = Pipeline([
    transport.input(),
    self.latency_analyzer,  # ← Tracks all frame timings
    stt,
    context_aggregator.user(),
    self.rtvi,
    llm,
    tts,
    transport.output(),
    context_aggregator.assistant(),
])
```

## Data Export

### JSON Format
Each interaction produces structured JSON data:

```json
{
  "interaction_id": "interaction_1_1704067200000",
  "stt_latency_ms": 150.25,
  "llm_latency_ms": 450.75,
  "tts_latency_ms": 120.50,
  "total_latency_ms": 850.00,
  "voice_to_voice_latency_ms": 721.25,
  "timestamps": {
    "start": 1704067200.0,
    "audio_received": 1704067200.1,
    "transcription_complete": 1704067200.25,
    "llm_complete": 1704067200.7,
    "tts_complete": 1704067200.82,
    "audio_output": 1704067200.85,
    "end": 1704067200.85
  }
}
```

### Log Mining
Search logs for structured data:
```bash
grep "LATENCY_METRICS:" your_log_file.log | jq .
```

## Performance Optimization Tips

### 🚀 **Improving Voice-to-Voice Latency**
1. **Optimize STT**: Use faster providers (Deepgram, Groq)
2. **Optimize LLM**: Use smaller models or faster providers
3. **Optimize TTS**: Use streaming TTS services
4. **Network**: Reduce geographic distance to services
5. **Infrastructure**: Use faster hardware/GPU acceleration

### 📊 **Monitoring Best Practices**
1. **Set Alerts**: Monitor P95 latencies, not just averages
2. **Track Trends**: Look for performance degradation over time
3. **A/B Testing**: Compare different configurations
4. **Load Testing**: Verify performance under load
5. **Geographic Testing**: Test from different locations

## Troubleshooting

### Common Issues

**High STT Latency:**
- Check network connectivity to STT provider
- Verify audio quality and format
- Consider switching providers

**High LLM Latency:**
- Reduce context size
- Use faster LLM models
- Implement prompt optimization

**High TTS Latency:**
- Use streaming TTS providers
- Optimize text length
- Consider caching for common responses

**Inconsistent Latency:**
- Check system resources (CPU, memory)
- Monitor network stability
- Verify service provider performance

### Debug Mode

Enable debug logging to see frame-by-frame timing:

```python
import logging
logging.getLogger("voice_assistant.services.latency_analyzer").setLevel(logging.DEBUG)
```

## API Reference

### Methods

- `get_latency_statistics()` - Get current statistics
- `reset_latency_statistics()` - Reset all statistics
- `log_latency_report()` - Generate comprehensive report
- `get_recent_latency_metrics(count=5)` - Get recent interactions

### Configuration

No additional configuration required - latency analysis is automatically enabled when using the VoiceAssistant class.

## Future Enhancements

- [ ] Real-time latency alerts
- [ ] Export to monitoring systems (Prometheus, Grafana)
- [ ] Machine learning-based latency prediction
- [ ] Component-specific optimization recommendations
- [ ] Integration with load testing tools 