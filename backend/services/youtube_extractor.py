"""
YouTube data extraction service
Handles all YouTube API interactions and video data extraction
"""

import os
import httpx
from typing import Optional, List
from dotenv import load_dotenv

from models.schemas import VideoMetadata
from utils.video_utils import extract_video_id, parse_iso8601_duration

load_dotenv()

# YouTube Data API v3 configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeAPIError(Exception):
    """Custom exception for YouTube API errors"""
    pass


async def get_metadata(video_id: str) -> VideoMetadata:
    """
    Fetch video metadata from YouTube Data API v3.
    
    API Endpoint: GET /youtube/v3/videos
    Documentation: https://developers.google.com/youtube/v3/docs/videos/list
    
    Args:
        video_id: YouTube video ID (11 characters)
        
    Returns:
        VideoMetadata: Pydantic model with video metadata
        
    Raises:
        YouTubeAPIError: If API request fails
        ValueError: If video not found or invalid video ID
        
    Example:
        >>> metadata = await get_metadata("dQw4w9WgXcQ")
        >>> print(metadata.title)
        'Rick Astley - Never Gonna Give You Up'
    """
    if not YOUTUBE_API_KEY:
        raise YouTubeAPIError(
            "YOUTUBE_API_KEY not found in environment variables. "
            "Please add it to backend/.env file."
        )
    
    # Build API request URL
    url = f"{YOUTUBE_API_BASE}/videos"
    params = {
        "part": "snippet,statistics,contentDetails",
        "id": video_id,
        "key": YOUTUBE_API_KEY
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        
        # Check if video exists
        if not data.get("items"):
            raise ValueError(f"Video not found: {video_id}")
        
        # Extract video data
        video_data = data["items"][0]
        snippet = video_data.get("snippet", {})
        statistics = video_data.get("statistics", {})
        content_details = video_data.get("contentDetails", {})
        
        # Parse duration from ISO 8601 format (e.g., "PT4M13S")
        duration_iso = content_details.get("duration", "PT0S")
        duration_seconds = parse_iso8601_duration(duration_iso)
        
        # Get thumbnail URL (prefer high quality)
        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = (
            thumbnails.get("high", {}).get("url") or
            thumbnails.get("medium", {}).get("url") or
            thumbnails.get("default", {}).get("url") or
            ""
        )
        
        # Build VideoMetadata model
        metadata = VideoMetadata(
            video_id=video_id,
            title=snippet.get("title", ""),
            description=snippet.get("description", ""),
            channel_name=snippet.get("channelTitle", ""),
            channel_id=snippet.get("channelId", ""),
            duration_seconds=duration_seconds,
            view_count=int(statistics.get("viewCount", 0)),
            like_count=int(statistics.get("likeCount", 0)) if statistics.get("likeCount") else None,
            tags=snippet.get("tags", []),
            thumbnail_url=thumbnail_url,
            published_at=snippet.get("publishedAt", ""),
            category_id=snippet.get("categoryId", "0")
        )
        
        return metadata
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            raise YouTubeAPIError(
                "YouTube API quota exceeded or invalid API key. "
                "Check your API key and quota at https://console.cloud.google.com"
            )
        elif e.response.status_code == 400:
            raise ValueError(f"Invalid video ID: {video_id}")
        else:
            raise YouTubeAPIError(f"YouTube API error: {e}")
    
    except httpx.RequestError as e:
        raise YouTubeAPIError(f"Network error while fetching metadata: {e}")
    
    except Exception as e:
        raise YouTubeAPIError(f"Unexpected error: {e}")


async def get_top_comments(video_id: str, max_results: int = 20) -> List[str]:
    """
    Fetch top comments from a YouTube video.
    
    API Endpoint: GET /youtube/v3/commentThreads
    Documentation: https://developers.google.com/youtube/v3/docs/commentThreads/list
    
    Args:
        video_id: YouTube video ID
        max_results: Maximum number of comments to fetch (default: 20)
        
    Returns:
        List[str]: List of comment texts
        
    Raises:
        YouTubeAPIError: If API request fails
        
    Note:
        Returns empty list if comments are disabled on the video
    """
    if not YOUTUBE_API_KEY:
        raise YouTubeAPIError("YOUTUBE_API_KEY not found in environment variables")
    
    url = f"{YOUTUBE_API_BASE}/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": min(max_results, 100),  # API max is 100
        "order": "relevance",  # Get most relevant comments
        "textFormat": "plainText",
        "key": YOUTUBE_API_KEY
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        
        # Extract comment texts
        comments = []
        for item in data.get("items", []):
            comment_text = (
                item.get("snippet", {})
                .get("topLevelComment", {})
                .get("snippet", {})
                .get("textDisplay", "")
            )
            if comment_text:
                comments.append(comment_text)
        
        return comments
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            # Comments might be disabled - return empty list
            return []
        else:
            raise YouTubeAPIError(f"Error fetching comments: {e}")
    
    except httpx.RequestError as e:
        raise YouTubeAPIError(f"Network error while fetching comments: {e}")
    
    except Exception as e:
        # Don't fail the entire extraction if comments fail
        print(f"Warning: Could not fetch comments: {e}")
        return []


async def get_metadata_from_url(youtube_url: str) -> VideoMetadata:
    """
    Convenience function to get metadata directly from YouTube URL.
    
    Args:
        youtube_url: YouTube video URL in any format
        
    Returns:
        VideoMetadata: Video metadata
        
    Raises:
        ValueError: If URL is invalid
        YouTubeAPIError: If API request fails
        
    Example:
        >>> metadata = await get_metadata_from_url("https://youtu.be/dQw4w9WgXcQ")
        >>> print(metadata.title)
    """
    video_id = extract_video_id(youtube_url)
    return await get_metadata(video_id)


# ============================================================================
# YT-DLP Integration for Captions and Audio
# ============================================================================

import subprocess
import json
from pathlib import Path


def get_captions(video_id: str) -> Optional[str]:
    """
    Extract video captions/subtitles using yt-dlp.
    
    Tries to get auto-generated captions in English.
    Falls back to any available subtitle language if English not available.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Optional[str]: Caption text if available, None otherwise
        
    Note:
        Uses yt-dlp command line tool for reliability
    """
    try:
        # Create temp directory for captions
        temp_dir = Path("/tmp/vidbrain")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = temp_dir / f"{video_id}.%(ext)s"
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # yt-dlp command to download subtitles only
        cmd = [
            "yt-dlp",
            "--write-auto-sub",  # Download auto-generated subs
            "--write-sub",       # Download manual subs if available
            "--sub-lang", "en",  # Prefer English
            "--skip-download",   # Don't download video
            "--sub-format", "vtt",  # WebVTT format
            "--output", str(output_path),
            video_url
        ]
        
        # Run yt-dlp
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Find the downloaded caption file
        caption_files = list(temp_dir.glob(f"{video_id}*.vtt"))
        
        if not caption_files:
            return None
        
        # Read caption file
        caption_file = caption_files[0]
        with open(caption_file, 'r', encoding='utf-8') as f:
            caption_text = f.read()
        
        # Clean up VTT formatting (remove timestamps and formatting tags)
        lines = caption_text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip VTT headers, timestamps, and empty lines
            if (line.strip() and 
                not line.startswith('WEBVTT') and
                not '-->' in line and
                not line.strip().isdigit()):
                # Remove HTML tags
                clean_line = line.replace('<c>', '').replace('</c>', '')
                cleaned_lines.append(clean_line.strip())
        
        # Clean up caption file
        caption_file.unlink()
        
        return ' '.join(cleaned_lines) if cleaned_lines else None
        
    except subprocess.TimeoutExpired:
        print(f"Warning: Caption extraction timed out for {video_id}")
        return None
    except Exception as e:
        print(f"Warning: Could not extract captions: {e}")
        return None


def download_audio(video_id: str) -> Optional[str]:
    """
    Download audio track from YouTube video using yt-dlp.
    
    Downloads audio in MP3 format for transcription.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Optional[str]: Path to downloaded audio file, None if failed
        
    Note:
        Caller is responsible for cleaning up the audio file after use
    """
    try:
        # Create temp directory
        temp_dir = Path("/tmp/vidbrain")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = temp_dir / f"{video_id}.mp3"
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # yt-dlp command to extract audio only
        cmd = [
            "yt-dlp",
            "-x",  # Extract audio
            "--audio-format", "mp3",  # Convert to MP3
            "--audio-quality", "5",  # Medium quality (0=best, 9=worst)
            "--output", str(output_path),
            video_url
        ]
        
        # Run yt-dlp
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes timeout
        )
        
        if result.returncode != 0:
            print(f"yt-dlp error: {result.stderr}")
            return None
        
        # Verify file exists
        if output_path.exists():
            return str(output_path)
        else:
            return None
            
    except subprocess.TimeoutExpired:
        print(f"Warning: Audio download timed out for {video_id}")
        return None
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None


def download_video(video_id: str, quality: str = "worst") -> Optional[str]:
    """
    Download video file from YouTube using yt-dlp.
    
    Downloads low-quality video for frame extraction to save bandwidth/time.
    
    Args:
        video_id: YouTube video ID
        quality: Video quality ("worst" for frame extraction, "best" for analysis)
        
    Returns:
        Optional[str]: Path to downloaded video file, None if failed
        
    Note:
        Caller is responsible for cleaning up the video file after use
    """
    try:
        # Create temp directory
        temp_dir = Path("/tmp/vidbrain")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = temp_dir / f"{video_id}.mp4"
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # yt-dlp command
        cmd = [
            "yt-dlp",
            "-f", f"{quality}[ext=mp4]",  # Prefer MP4 format
            "--output", str(output_path),
            video_url
        ]
        
        # Run yt-dlp
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180  # 3 minutes timeout
        )
        
        if result.returncode != 0:
            print(f"yt-dlp error: {result.stderr}")
            return None
        
        # Verify file exists
        if output_path.exists():
            return str(output_path)
        else:
            return None
            
    except subprocess.TimeoutExpired:
        print(f"Warning: Video download timed out for {video_id}")
        return None
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None


# ============================================================================
# Orchestrator: Complete Extraction Pipeline
# ============================================================================

import time
from models.schemas import ExtractionResult
from services.transcriber import transcribe_audio
from services.frame_analyzer import extract_key_frames


async def extract_all(youtube_url: str) -> ExtractionResult:
    """
    Master extraction pipeline - combines all extraction modules.
    
    Extracts everything we need from a YouTube video:
    1. Video metadata (title, duration, views, etc.)
    2. Captions/subtitles (if available)
    3. Audio transcription (fallback if no captions)
    4. Key video frames
    5. Top comments
    
    Each step can fail independently - we continue with others.
    
    Args:
        youtube_url: YouTube video URL in any format
        
    Returns:
        ExtractionResult: Complete extraction result
        
    Raises:
        ValueError: If URL is invalid
        YouTubeAPIError: If critical API calls fail
        
    Example:
        >>> result = await extract_all("https://youtu.be/dQw4w9WgXcQ")
        >>> print(result.metadata.title)
        'Rick Astley - Never Gonna Give You Up'
        >>> print(len(result.key_frame_paths))
        7
    """
    start_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"Starting extraction for: {youtube_url}")
    print(f"{'='*60}\n")
    
    # Step 1: Extract video ID from URL
    print("Step 1/7: Extracting video ID...")
    video_id = extract_video_id(youtube_url)
    print(f"✓ Video ID: {video_id}\n")
    
    # Step 2: Get metadata (CRITICAL - must succeed)
    print("Step 2/7: Fetching metadata from YouTube API...")
    metadata = await get_metadata(video_id)
    print(f"✓ Title: {metadata.title}")
    print(f"✓ Duration: {metadata.duration_seconds}s")
    print(f"✓ Views: {metadata.view_count:,}\n")
    
    # Step 3: Get captions (optional - OK if fails)
    print("Step 3/7: Extracting captions...")
    captions = None
    try:
        captions = get_captions(video_id)
        if captions:
            print(f"✓ Captions extracted: {len(captions)} characters\n")
        else:
            print("⚠ No captions available - will use transcription\n")
    except Exception as e:
        print(f"⚠ Caption extraction failed: {e}\n")
    
    # Step 4: Download audio (for transcription if no captions)
    transcript = None
    audio_path = None
    
    if not captions:
        print("Step 4/7: Downloading audio for transcription...")
        try:
            audio_path = download_audio(video_id)
            if audio_path:
                print(f"✓ Audio downloaded: {audio_path}\n")
                
                # Step 5: Transcribe audio
                print("Step 5/7: Transcribing audio with Whisper...")
                print("⏳ This may take a while (local Whisper on CPU)...")
                transcript = transcribe_audio(audio_path)
                if transcript:
                    print(f"✓ Transcription complete: {len(transcript)} characters\n")
                else:
                    print("⚠ Transcription failed\n")
            else:
                print("⚠ Audio download failed\n")
        except Exception as e:
            print(f"⚠ Audio processing failed: {e}\n")
    else:
        print("Step 4-5/7: Skipping audio download/transcription (captions available)\n")
    
    # Step 6: Extract key frames
    print("Step 6/7: Extracting key frames...")
    key_frames = []
    video_path = None
    
    try:
        video_path = download_video(video_id, quality="worst")
        if video_path:
            print(f"✓ Video downloaded: {video_path}")
            key_frames = extract_key_frames(video_path, interval_seconds=30)
            print(f"✓ Extracted {len(key_frames)} frames\n")
        else:
            print("⚠ Video download failed - no frames extracted\n")
    except Exception as e:
        print(f"⚠ Frame extraction failed: {e}\n")
    
    # Step 7: Get top comments
    print("Step 7/7: Fetching top comments...")
    comments = []
    try:
        comments = await get_top_comments(video_id, max_results=20)
        print(f"✓ Fetched {len(comments)} comments\n")
    except Exception as e:
        print(f"⚠ Comment extraction failed: {e}\n")
    
    # Cleanup temporary files
    print("Cleaning up temporary files...")
    try:
        if audio_path and Path(audio_path).exists():
            Path(audio_path).unlink()
            print(f"✓ Deleted audio file")
        
        if video_path and Path(video_path).exists():
            Path(video_path).unlink()
            print(f"✓ Deleted video file")
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")
    
    # Calculate extraction time
    extraction_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"Extraction complete in {extraction_time:.1f} seconds")
    print(f"{'='*60}\n")
    
    # Build and return result
    return ExtractionResult(
        metadata=metadata,
        captions=captions,
        transcript=transcript,
        key_frame_paths=key_frames,
        top_comments=comments,
        extraction_time_seconds=extraction_time
    )
