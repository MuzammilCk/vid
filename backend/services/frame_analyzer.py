"""
Video frame extraction and analysis service
Extracts key frames from videos using OpenCV
"""

import cv2
import numpy as np
from typing import List, Optional
from pathlib import Path


def extract_key_frames(
    video_path: str,
    interval_seconds: int = 30,
    max_width: int = 1280
) -> List[str]:
    """
    Extract key frames from video at regular intervals.
    
    Extracts one frame every N seconds for AI analysis.
    Frames are resized to save memory and speed up AI processing.
    
    Args:
        video_path: Path to video file
        interval_seconds: Seconds between frame extractions (default: 30)
        max_width: Maximum frame width in pixels (default: 1280 for 720p)
        
    Returns:
        List[str]: Paths to extracted frame images
        
    Example:
        >>> frames = extract_key_frames("/tmp/vidbrain/video.mp4", interval_seconds=30)
        >>> print(f"Extracted {len(frames)} frames")
        Extracted 20 frames
        
    Note:
        For a 10-minute video with 30s intervals: 20 frames
        For a 1-hour video with 30s intervals: 120 frames
    """
    try:
        # Verify video file exists
        video_file = Path(video_path)
        if not video_file.exists():
            print(f"Error: Video file not found: {video_path}")
            return []
        
        # Create output directory
        video_id = video_file.stem  # Filename without extension
        output_dir = video_file.parent / video_id
        output_dir.mkdir(exist_ok=True)
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            print(f"Error: Could not open video: {video_path}")
            return []
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_seconds = total_frames / fps if fps > 0 else 0
        
        print(f"Video: {duration_seconds:.1f}s, {fps:.1f} FPS, {total_frames} frames")
        
        # Calculate frame interval
        frame_interval = int(fps * interval_seconds)
        
        if frame_interval == 0:
            print("Error: Invalid frame interval")
            cap.release()
            return []
        
        # Extract frames
        frame_paths = []
        frame_count = 0
        saved_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Save frame at intervals
            if frame_count % frame_interval == 0:
                # Resize frame if needed
                height, width = frame.shape[:2]
                
                if width > max_width:
                    # Calculate new dimensions maintaining aspect ratio
                    scale = max_width / width
                    new_width = max_width
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # Save frame as JPEG
                frame_filename = f"frame_{saved_count + 1:03d}.jpg"
                frame_path = output_dir / frame_filename
                
                cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_paths.append(str(frame_path))
                saved_count += 1
            
            frame_count += 1
        
        # Release video capture
        cap.release()
        
        print(f"Extracted {saved_count} frames from video")
        return frame_paths
        
    except Exception as e:
        print(f"Error extracting frames: {e}")
        return []


def extract_frames_at_timestamps(
    video_path: str,
    timestamps: List[float],
    max_width: int = 1280
) -> List[str]:
    """
    Extract frames at specific timestamps.
    
    Useful for Phase 2+ when we want frames at specific moments
    (e.g., when certain keywords are mentioned in transcript).
    
    Args:
        video_path: Path to video file
        timestamps: List of timestamps in seconds
        max_width: Maximum frame width in pixels
        
    Returns:
        List[str]: Paths to extracted frame images
        
    Example:
        >>> frames = extract_frames_at_timestamps("/tmp/video.mp4", [10.5, 30.2, 60.0])
        >>> print(f"Extracted {len(frames)} frames")
    """
    try:
        video_file = Path(video_path)
        if not video_file.exists():
            return []
        
        # Create output directory
        video_id = video_file.stem
        output_dir = video_file.parent / video_id
        output_dir.mkdir(exist_ok=True)
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return []
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_paths = []
        
        for idx, timestamp in enumerate(timestamps):
            # Seek to timestamp
            frame_number = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Resize if needed
            height, width = frame.shape[:2]
            if width > max_width:
                scale = max_width / width
                new_width = max_width
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Save frame
            frame_filename = f"frame_t{int(timestamp):04d}.jpg"
            frame_path = output_dir / frame_filename
            cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_paths.append(str(frame_path))
        
        cap.release()
        return frame_paths
        
    except Exception as e:
        print(f"Error extracting frames at timestamps: {e}")
        return []


def frames_to_base64(frame_paths: List[str]) -> List[str]:
    """
    Convert frame images to base64 strings for AI API.
    
    Gemini API accepts images as base64-encoded strings.
    
    Args:
        frame_paths: List of paths to frame images
        
    Returns:
        List[str]: Base64-encoded image strings
        
    Note:
        This will be used in Phase 2 for sending frames to Gemini
    """
    import base64
    
    base64_frames = []
    
    for frame_path in frame_paths:
        try:
            with open(frame_path, 'rb') as f:
                image_data = f.read()
                base64_str = base64.b64encode(image_data).decode('utf-8')
                base64_frames.append(base64_str)
        except Exception as e:
            print(f"Error encoding frame {frame_path}: {e}")
            continue
    
    return base64_frames
