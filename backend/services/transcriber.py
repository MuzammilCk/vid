"""
Audio transcription service using OpenAI Whisper
Converts audio files to text for video analysis
"""

from typing import Optional
from pathlib import Path

# Make Whisper optional for testing
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: Whisper not installed. Transcription will not be available.")


# Load Whisper model (lazy loading)
_whisper_model = None


def get_whisper_model(model_name: str = "base"):
    """
    Get or load Whisper model (singleton pattern for efficiency).
    
    Available models: tiny, base, small, medium, large
    - tiny: fastest, least accurate
    - base: good balance (recommended for Phase 1)
    - small: better accuracy, slower
    - medium/large: best accuracy, very slow on CPU
    
    Args:
        model_name: Whisper model size
        
    Returns:
        Whisper model instance
    """
    if not WHISPER_AVAILABLE:
        raise ImportError("Whisper is not installed. Install with: pip install openai-whisper")
    
    global _whisper_model
    
    if _whisper_model is None:
        print(f"Loading Whisper model '{model_name}'...")
        _whisper_model = whisper.load_model(model_name)
        print("Whisper model loaded successfully")
    
    return _whisper_model


def transcribe_audio(file_path: str, model_name: str = "base") -> Optional[str]:
    """
    Transcribe audio file to text using OpenAI Whisper.
    
    Uses local Whisper model (no API calls, completely free).
    Performance: ~1 minute per minute of audio on CPU.
    
    Args:
        file_path: Path to audio file (MP3, WAV, etc.)
        model_name: Whisper model size (default: "base")
        
    Returns:
        Optional[str]: Transcribed text, None if transcription fails
        
    Example:
        >>> text = transcribe_audio("/tmp/vidbrain/dQw4w9WgXcQ.mp3")
        >>> print(text[:100])
        "We're no strangers to love, you know the rules and so do I..."
        
    Note:
        This function can be slow on CPU. For production, consider:
        - Using OpenAI Whisper API (faster, costs $0.006/minute)
        - Running on GPU for 10x speedup
        - Caching transcriptions in database
    """
    try:
        # Verify file exists
        audio_path = Path(file_path)
        if not audio_path.exists():
            print(f"Error: Audio file not found: {file_path}")
            return None
        
        # Load Whisper model
        model = get_whisper_model(model_name)
        
        # Transcribe audio
        print(f"Transcribing audio: {file_path}")
        result = model.transcribe(str(audio_path))
        
        # Extract text from result
        transcription = result.get("text", "").strip()
        
        if not transcription:
            print("Warning: Transcription returned empty text")
            return None
        
        print(f"Transcription complete: {len(transcription)} characters")
        return transcription
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None


def transcribe_audio_with_timestamps(file_path: str, model_name: str = "base") -> Optional[dict]:
    """
    Transcribe audio with word-level timestamps.
    
    Useful for Phase 2+ when we need to sync transcription with video frames.
    
    Args:
        file_path: Path to audio file
        model_name: Whisper model size
        
    Returns:
        Optional[dict]: Whisper result dict with segments and timestamps
        
    Example:
        >>> result = transcribe_audio_with_timestamps("/tmp/audio.mp3")
        >>> for segment in result["segments"]:
        ...     print(f"{segment['start']:.2f}s: {segment['text']}")
    """
    try:
        audio_path = Path(file_path)
        if not audio_path.exists():
            return None
        
        model = get_whisper_model(model_name)
        result = model.transcribe(str(audio_path))
        
        return result
        
    except Exception as e:
        print(f"Error during transcription with timestamps: {e}")
        return None
