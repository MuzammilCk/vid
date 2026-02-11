"""
Analysis router for VidBrain AI
Handles video analysis requests with extraction and classification
"""

from fastapi import APIRouter, HTTPException
from models.schemas import AnalyzeRequest, AnalyzeResponse, JobStatus
from services.youtube_extractor import extract_all, YouTubeAPIError
from services.classifier import classify_with_fallback
import uuid

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_video(request: AnalyzeRequest):
    """
    Analyze a YouTube video: extract data + classify category.
    
    This endpoint:
    1. Extracts video metadata
    2. Gets captions or transcribes audio
    3. Extracts key frames
    4. Fetches top comments
    5. Classifies video using AI (Gemini) with fallback
    
    Args:
        request: AnalyzeRequest with youtube_url
        
    Returns:
        AnalyzeResponse: Complete analysis result with classification
        
    Example:
        POST /analyze
        {
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    try:
        # Step 1: Run extraction pipeline
        print(f"\n{'='*60}")
        print(f"Job {job_id}: Starting analysis")
        print(f"{'='*60}\n")
        
        extraction_result = await extract_all(request.youtube_url)
        
        # Step 2: Classify video using AI with fallback
        print(f"\n{'='*60}")
        print(f"Job {job_id}: Classifying video")
        print(f"{'='*60}\n")
        
        classification_result = await classify_with_fallback(extraction_result)
        
        print(f"\n{'='*60}")
        print(f"Job {job_id}: Analysis complete")
        print(f"Category: {classification_result.category.value}")
        print(f"Confidence: {classification_result.confidence:.2f}")
        print(f"Model: {classification_result.model_used}")
        print(f"{'='*60}\n")
        
        # Return successful response
        return AnalyzeResponse(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            category=classification_result.category,
            metadata=extraction_result.metadata,
            result=extraction_result,
            error=None
        )
        
    except ValueError as e:
        # Invalid URL or video ID
        raise HTTPException(
            status_code=400,
            detail=f"Invalid YouTube URL: {str(e)}"
        )
    
    except YouTubeAPIError as e:
        # YouTube API error
        raise HTTPException(
            status_code=500,
            detail=f"YouTube API error: {str(e)}"
        )
    
    except Exception as e:
        # Unexpected error
        print(f"Error in analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
