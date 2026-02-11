"""
Video utility functions for VidBrain AI
Handles YouTube URL parsing and video ID extraction
"""

import re
from typing import Optional
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from various URL formats.
    
    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    
    Args:
        url: YouTube video URL in any supported format
        
    Returns:
        str: 11-character YouTube video ID
        
    Raises:
        ValueError: If URL is invalid or video ID cannot be extracted
        
    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    # Clean up URL
    url = url.strip()
    
    # Pattern 1: youtu.be/VIDEO_ID
    if "youtu.be/" in url:
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
    
    # Pattern 2: youtube.com/shorts/VIDEO_ID
    if "/shorts/" in url:
        match = re.search(r'/shorts/([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
    
    # Pattern 3: youtube.com/embed/VIDEO_ID
    if "/embed/" in url:
        match = re.search(r'/embed/([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
    
    # Pattern 4: youtube.com/v/VIDEO_ID
    if "/v/" in url:
        match = re.search(r'/v/([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
    
    # Pattern 5: youtube.com/watch?v=VIDEO_ID (most common)
    if "youtube.com" in url or "m.youtube.com" in url:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        if 'v' in query_params:
            video_id = query_params['v'][0]
            # Validate video ID format (11 characters, alphanumeric + _ -)
            if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                return video_id
    
    # If no pattern matched, raise error
    raise ValueError(
        f"Could not extract video ID from URL: {url}. "
        "Please provide a valid YouTube URL."
    )


def validate_video_id(video_id: str) -> bool:
    """
    Validate that a string is a valid YouTube video ID.
    
    Args:
        video_id: String to validate
        
    Returns:
        bool: True if valid video ID format, False otherwise
        
    Examples:
        >>> validate_video_id("dQw4w9WgXcQ")
        True
        >>> validate_video_id("invalid")
        False
    """
    if not video_id or not isinstance(video_id, str):
        return False
    
    # YouTube video IDs are exactly 11 characters: alphanumeric, underscore, hyphen
    return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration (e.g., "3:45", "1:23:45")
        
    Examples:
        >>> format_duration(225)
        '3:45'
        >>> format_duration(3665)
        '1:01:05'
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def parse_iso8601_duration(duration: str) -> int:
    """
    Parse ISO 8601 duration format (from YouTube API) to seconds.
    
    YouTube API returns duration as: PT#H#M#S (e.g., PT4M13S = 4 minutes 13 seconds)
    
    Args:
        duration: ISO 8601 duration string
        
    Returns:
        int: Duration in seconds
        
    Examples:
        >>> parse_iso8601_duration("PT4M13S")
        253
        >>> parse_iso8601_duration("PT1H2M3S")
        3723
    """
    # Remove PT prefix
    duration = duration.replace("PT", "")
    
    hours = 0
    minutes = 0
    seconds = 0
    
    # Extract hours
    if "H" in duration:
        hours_match = re.search(r'(\d+)H', duration)
        if hours_match:
            hours = int(hours_match.group(1))
    
    # Extract minutes
    if "M" in duration:
        minutes_match = re.search(r'(\d+)M', duration)
        if minutes_match:
            minutes = int(minutes_match.group(1))
    
    # Extract seconds
    if "S" in duration:
        seconds_match = re.search(r'(\d+)S', duration)
        if seconds_match:
            seconds = int(seconds_match.group(1))
    
    return hours * 3600 + minutes * 60 + seconds
