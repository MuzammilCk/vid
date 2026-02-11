"""
Pydantic models for VidBrain AI
Defines all data structures for video extraction and analysis
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from enum import Enum
from datetime import datetime


class VideoCategory(str, Enum):
    """Video content categories for AI classification"""
    MOVIE_LIST = "movie_list"
    SONG_LIST = "song_list"
    COMEDY = "comedy"
    RECIPE = "recipe"
    EDUCATION = "education"
    PRODUCT_REVIEW = "product_review"
    TRAVEL = "travel"
    NEWS = "news"
    FITNESS = "fitness"
    PODCAST = "podcast"
    TUTORIAL = "tutorial"
    GAMING = "gaming"
    VLOG = "vlog"
    UNKNOWN = "unknown"


class VideoMetadata(BaseModel):
    """YouTube video metadata from YouTube Data API v3"""
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    description: str = Field(..., description="Video description")
    channel_name: str = Field(..., description="Channel name")
    channel_id: str = Field(..., description="YouTube channel ID")
    duration_seconds: int = Field(..., description="Video duration in seconds")
    view_count: int = Field(default=0, description="Number of views")
    like_count: Optional[int] = Field(default=None, description="Number of likes")
    tags: List[str] = Field(default_factory=list, description="Video tags")
    thumbnail_url: str = Field(..., description="Thumbnail image URL")
    published_at: str = Field(..., description="Publication date (ISO 8601)")
    category_id: str = Field(..., description="YouTube's category ID")

    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "title": "Rick Astley - Never Gonna Give You Up",
                "description": "The official video for...",
                "channel_name": "Rick Astley",
                "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
                "duration_seconds": 212,
                "view_count": 1400000000,
                "like_count": 15000000,
                "tags": ["rick astley", "never gonna give you up"],
                "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                "published_at": "2009-10-25T06:57:33Z",
                "category_id": "10"
            }
        }


class ExtractionResult(BaseModel):
    """Complete extraction result from YouTube video"""
    metadata: VideoMetadata
    captions: Optional[str] = Field(
        default=None,
        description="Video captions/subtitles if available"
    )
    transcript: Optional[str] = Field(
        default=None,
        description="Audio transcription from Whisper (fallback if no captions)"
    )
    key_frame_paths: List[str] = Field(
        default_factory=list,
        description="Local file paths to extracted key frames"
    )
    top_comments: List[str] = Field(
        default_factory=list,
        description="Top comments for context"
    )
    extraction_time_seconds: Optional[float] = Field(
        default=None,
        description="Time taken to extract all data"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "video_id": "dQw4w9WgXcQ",
                    "title": "Rick Astley - Never Gonna Give You Up",
                    "duration_seconds": 212
                },
                "captions": "We're no strangers to love...",
                "transcript": None,
                "key_frame_paths": [
                    "/tmp/vidbrain/dQw4w9WgXcQ/frame_001.jpg",
                    "/tmp/vidbrain/dQw4w9WgXcQ/frame_002.jpg"
                ],
                "top_comments": [
                    "Never gonna give you up!",
                    "Classic song"
                ],
                "extraction_time_seconds": 45.2
            }
        }


class AnalyzeRequest(BaseModel):
    """Request to analyze a YouTube video"""
    youtube_url: str = Field(
        ...,
        description="YouTube video URL (any format)",
        examples=[
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        ]
    )


class JobStatus(str, Enum):
    """Job processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalyzeResponse(BaseModel):
    """Response from video analysis"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    category: Optional[VideoCategory] = Field(
        default=None,
        description="Detected video category (Phase 2)"
    )
    metadata: Optional[VideoMetadata] = Field(
        default=None,
        description="Video metadata"
    )
    result: Optional[ExtractionResult] = Field(
        default=None,
        description="Complete extraction result (when status=completed)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if status=failed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "category": "song_list",
                "metadata": {
                    "video_id": "dQw4w9WgXcQ",
                    "title": "Rick Astley - Never Gonna Give You Up"
                },
                "result": {
                    "metadata": {},
                    "captions": "...",
                    "key_frame_paths": []
                },
                "error": None
            }
        }


class ClassificationResult(BaseModel):
    """Result of AI video classification"""
    video_id: str = Field(..., description="YouTube video ID")
    category: VideoCategory = Field(..., description="Classified category")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Classification confidence score (0-1)"
    )
    sub_category: Optional[str] = Field(
        default=None,
        description="More specific sub-category if applicable"
    )
    reasoning: str = Field(
        ...,
        description="Explanation for the classification decision"
    )
    alternative_categories: List[str] = Field(
        default_factory=list,
        description="Alternative category suggestions"
    )
    model_used: str = Field(
        default="gemini-2.0-flash-exp",
        description="AI model used for classification"
    )
    classified_at: Optional[str] = Field(
        default=None,
        description="Timestamp of classification (ISO 8601)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "category": "song_list",
                "confidence": 0.92,
                "sub_category": "80s music compilation",
                "reasoning": "Video title mentions 'Never Gonna Give You Up', transcript shows song lyrics, and visual frames show music video content",
                "alternative_categories": ["vlog", "comedy"],
                "model_used": "gemini-2.0-flash-exp",
                "classified_at": "2024-02-12T03:15:00Z"
            }
        }
