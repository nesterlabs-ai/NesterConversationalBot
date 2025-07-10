"""Example script demonstrating latency analysis usage with VoiceAssistant.

This script shows how to:
1. Access latency statistics
2. Monitor performance in real-time
3. Generate reports
4. Reset statistics
"""

import asyncio
import json
from voice_assistant import VoiceAssistant
from config import get_assistant_config

async def main():
    """Demonstrate latency analysis features."""
    
    # Create voice assistant with latency analysis enabled
    config = get_assistant_config()
    assistant = VoiceAssistant(config)
    
    print("🚀 Voice Assistant with Latency Analysis")
    print("=" * 50)
    
    # Initialize services
    assistant.initialize_services()
    
    # Example 1: Get initial statistics (should be empty)
    print("\n📊 Initial Latency Statistics:")
    stats = assistant.get_latency_statistics()
    print(json.dumps(stats, indent=2))
    
    # Example 2: Monitor service status including latency analyzer
    print("\n🔍 Service Status:")
    service_status = assistant.get_service_status()
    print(f"Latency Analyzer: {service_status['latency_analyzer']['initialized']}")
    
    # Example 3: Show how to access statistics during runtime
    print("\n📈 How to access latency metrics during runtime:")
    print("""
    # Get current statistics
    stats = assistant.get_latency_statistics()
    
    # Get recent interaction metrics
    recent_metrics = assistant.get_recent_latency_metrics(count=3)
    
    # Generate and log a comprehensive report
    assistant.log_latency_report()
    
    # Reset statistics (useful for testing)
    assistant.reset_latency_statistics()
    """)
    
    # Example 4: Show expected output format
    print("\n📋 Expected Latency Metrics Format:")
    example_metrics = {
        "interaction_id": "interaction_1_1234567890",
        "stt_latency_ms": 150.25,
        "llm_latency_ms": 450.75,
        "tts_latency_ms": 120.50,
        "total_latency_ms": 850.00,
        "voice_to_voice_latency_ms": 721.25,
        "timestamps": {
            "start": 1234567890.0,
            "audio_received": 1234567890.1,
            "transcription_complete": 1234567890.25,
            "llm_complete": 1234567890.7,
            "tts_complete": 1234567890.82,
            "audio_output": 1234567890.85,
            "end": 1234567890.85
        }
    }
    print(json.dumps(example_metrics, indent=2))
    
    print("\n🎯 Key Latency Metrics Explained:")
    print("• Voice-to-Voice: User stops speaking → Bot starts speaking")
    print("• STT Latency: Speech-to-text processing time")
    print("• LLM Latency: Language model response generation time")
    print("• TTS Latency: Text-to-speech conversion time")
    print("• Total Latency: Complete interaction processing time")
    
    print("\n📊 Performance Targets:")
    print("• Voice-to-Voice: < 800ms (excellent), < 1200ms (good)")
    print("• STT: < 300ms (excellent), < 500ms (good)")
    print("• LLM: < 500ms (excellent), < 1000ms (good)")
    print("• TTS: < 200ms (excellent), < 400ms (good)")
    
    print("\n🔄 Automatic Features:")
    print("• Latency tracking runs automatically in the pipeline")
    print("• Statistics are logged every 5 minutes")
    print("• Final report is generated when assistant shuts down")
    print("• Each interaction gets a unique ID for tracking")
    
    print("\n✅ Integration Complete!")
    print("The latency analyzer is now integrated into your voice assistant.")
    print("Run your assistant normally and check the logs for latency metrics.")

if __name__ == "__main__":
    asyncio.run(main()) 