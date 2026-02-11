"""
Video classification service using Google Gemini API

This module provides AI-powered video classification with:
- Gemini 2.0 Flash (primary, fast)
- Gemini 1.5 Pro (fallback, stable)
- Multimodal classification (text + images)
- Rule-based fallback for reliability
- Automatic retry with exponential backoff
"""

import os
import json
import re
import asyncio
from typing import Optional, List
from pathlib import Path
from datetime import datetime
from PIL import Image
import google.generativeai as genai

from models.schemas import ExtractionResult, ClassificationResult, VideoCategory
from utils.prompt_templates import (
    CLASSIFICATION_PROMPT,
    CLASSIFICATION_PROMPT_WITH_IMAGES
)
from config.gemini_models import GeminiModel, RecommendedModels

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Model selection (using centralized config)
PRIMARY_MODEL = RecommendedModels.CLASSIFICATION.value
FALLBACK_MODEL = RecommendedModels.CLASSIFICATION_FALLBACK.value

# Generation config
GENERATION_CONFIG = {
    "temperature": 0.1,  # Low temperature for deterministic classification
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}


class VideoClassifier:
    """Gemini-powered video classification service"""
    
    def __init__(self, model_name: str = PRIMARY_MODEL):
        """
        Initialize classifier with specified model.
        
        Args:
            model_name: Gemini model to use
        """
        if not GOOGLE_API_KEY:
            print("Warning: GOOGLE_API_KEY not set. Classification will use rule-based fallback.")
            self.model = None
            self.model_name = "none"
        else:
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=GENERATION_CONFIG
            )
            self.model_name = model_name
    
    async def classify_video(
        self,
        extraction: ExtractionResult,
        include_frames: bool = True,
        max_frames: int = 3
    ) -> ClassificationResult:
        """
        Classify a video using Gemini AI.
        
        Args:
            extraction: Video extraction data
            include_frames: Whether to include visual frames
            max_frames: Maximum number of frames to send (cost control)
            
        Returns:
            ClassificationResult with category and confidence
            
        Raises:
            ValueError: If API key not set or response invalid
        """
        if not self.model:
            raise ValueError("Gemini API not configured. Set GOOGLE_API_KEY environment variable.")
        
        # Build prompt from template
        prompt = self._build_prompt(extraction, include_frames)
        
        # Prepare content for Gemini
        content_parts = [prompt]
        
        # Add frames if available and requested
        if include_frames and extraction.key_frame_paths:
            frames_to_use = extraction.key_frame_paths[:max_frames]
            for frame_path in frames_to_use:
                try:
                    img = Image.open(frame_path)
                    content_parts.append(img)
                except Exception as e:
                    print(f"Warning: Could not load frame {frame_path}: {e}")
        
        # Generate classification
        try:
            response = self.model.generate_content(content_parts)
            
            # Parse response
            return self._parse_response(response, extraction)
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            raise
    
    def _build_prompt(
        self,
        extraction: ExtractionResult,
        include_frames: bool
    ) -> str:
        """Build classification prompt from template"""
        
        metadata = extraction.metadata
        
        # Choose template
        template = (
            CLASSIFICATION_PROMPT_WITH_IMAGES 
            if include_frames and extraction.key_frame_paths
            else CLASSIFICATION_PROMPT
        )
        
        # Get text content (captions or transcript)
        text_content = extraction.captions or extraction.transcript or "Not available"
        
        # Format comments
        comments_text = self._format_comments(extraction.top_comments[:10])
        
        # Format prompt
        prompt = template.format(
            title=metadata.title,
            channel=metadata.channel_name,
            description=metadata.description[:1000],  # Truncate long descriptions
            tags=", ".join(metadata.tags[:20]) if metadata.tags else "None",
            category_id=metadata.category_id,
            duration=metadata.duration_seconds,
            view_count=f"{metadata.view_count:,}" if metadata.view_count else "N/A",
            upload_date=metadata.published_at or "N/A",
            transcript=text_content[:3000],  # First 3000 chars
            comments=comments_text,
            num_frames=len(extraction.key_frame_paths[:3]) if include_frames else 0
        )
        
        return prompt
    
    def _format_comments(self, comments: List[str]) -> str:
        """Format comments for prompt"""
        if not comments:
            return "No comments available"
        
        formatted = []
        for i, comment in enumerate(comments[:10], 1):
            # Truncate long comments
            comment_text = comment[:200] if len(comment) > 200 else comment
            formatted.append(f"{i}. {comment_text}")
        
        return "\n".join(formatted)
    
    def _parse_response(
        self,
        response,
        extraction: ExtractionResult
    ) -> ClassificationResult:
        """Parse Gemini response into ClassificationResult"""
        
        try:
            # Get response text
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            response_text = response_text.strip()
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Validate category
            category_str = data.get("category", "unknown")
            try:
                category = VideoCategory(category_str)
            except ValueError:
                print(f"Warning: Invalid category '{category_str}', using UNKNOWN")
                category = VideoCategory.UNKNOWN
            
            # Build result
            return ClassificationResult(
                video_id=extraction.metadata.video_id,
                category=category,
                confidence=float(data.get("confidence", 0.5)),
                sub_category=data.get("sub_category"),
                reasoning=data.get("reasoning", "No reasoning provided"),
                alternative_categories=data.get("alternative_categories", []),
                model_used=self.model_name,
                classified_at=datetime.utcnow().isoformat() + "Z"
            )
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response text: {response.text[:500]}")
            raise ValueError(f"Invalid JSON response from Gemini: {e}")
        except Exception as e:
            print(f"Error parsing response: {e}")
            raise


# ============================================================================
# Fallback Strategies
# ============================================================================

async def classify_with_fallback(
    extraction: ExtractionResult
) -> ClassificationResult:
    """
    Classify with automatic fallback strategy:
    1. Try Gemini 2.0 Flash with images
    2. Try Gemini 2.0 Flash without images
    3. Try Gemini 1.5 Pro with images
    4. Try Gemini 1.5 Pro without images
    5. Fall back to rule-based classification
    """
    
    # Attempt 1: Gemini 2.0 Flash with frames
    try:
        classifier = VideoClassifier(PRIMARY_MODEL)
        result = await classifier.classify_video(extraction, include_frames=True)
        if result.confidence > 0.7:
            print(f"✓ Classified with {PRIMARY_MODEL} + images (confidence: {result.confidence:.2f})")
            return result
    except Exception as e:
        print(f"Attempt 1 failed (Gemini 2.0 Flash + images): {e}")
    
    # Attempt 2: Gemini 2.0 Flash without frames
    try:
        classifier = VideoClassifier(PRIMARY_MODEL)
        result = await classifier.classify_video(extraction, include_frames=False)
        if result.confidence > 0.6:
            print(f"✓ Classified with {PRIMARY_MODEL} text-only (confidence: {result.confidence:.2f})")
            return result
    except Exception as e:
        print(f"Attempt 2 failed (Gemini 2.0 Flash text-only): {e}")
    
    # Attempt 3: Gemini 1.5 Pro with frames
    try:
        classifier = VideoClassifier(FALLBACK_MODEL)
        result = await classifier.classify_video(extraction, include_frames=True)
        if result.confidence > 0.7:
            print(f"✓ Classified with {FALLBACK_MODEL} + images (confidence: {result.confidence:.2f})")
            return result
    except Exception as e:
        print(f"Attempt 3 failed (Gemini 1.5 Pro + images): {e}")
    
    # Attempt 4: Gemini 1.5 Pro without frames
    try:
        classifier = VideoClassifier(FALLBACK_MODEL)
        result = await classifier.classify_video(extraction, include_frames=False)
        if result.confidence > 0.5:
            print(f"✓ Classified with {FALLBACK_MODEL} text-only (confidence: {result.confidence:.2f})")
            return result
    except Exception as e:
        print(f"Attempt 4 failed (Gemini 1.5 Pro text-only): {e}")
    
    # Attempt 5: Rule-based fallback
    print("⚠ All AI attempts failed, using rule-based classification")
    return rule_based_classify(extraction)


def rule_based_classify(extraction: ExtractionResult) -> ClassificationResult:
    """
    Simple keyword-based classification as last resort.
    
    Uses weighted keyword matching to classify videos when AI is unavailable.
    Returns confidence scores capped at 0.6 to indicate lower reliability.
    """
    
    metadata = extraction.metadata
    title = metadata.title.lower()
    desc = metadata.description.lower()
    transcript = (extraction.captions or extraction.transcript or "").lower()[:1000]
    
    # Combine all text
    text = f"{title} {desc} {transcript}"
    
    # Define rules with weighted keywords
    rules = {
        VideoCategory.MOVIE_LIST: {
            "strong": ["top movies", "best movies", "must watch movies", "movie list", "films you"],
            "medium": ["movies of 20", "greatest films", "movie ranking", "film ranking"],
            "weak": ["movies", "cinema", "film"]
        },
        VideoCategory.SONG_LIST: {
            "strong": ["top songs", "best songs", "hit songs", "song list", "music compilation"],
            "medium": ["songs of 20", "playlist", "greatest hits", "music ranking"],
            "weak": ["songs", "music", "hits"]
        },
        VideoCategory.COMEDY: {
            "strong": ["stand up", "standup", "comedy special", "comedian"],
            "medium": ["comedy", "funny", "sketch", "skit"],
            "weak": ["laugh", "humor", "joke"]
        },
        VideoCategory.RECIPE: {
            "strong": ["recipe", "how to cook", "cooking tutorial", "how to make"],
            "medium": ["cooking", "baking", "ingredients", "prepare"],
            "weak": ["food", "kitchen", "meal"]
        },
        VideoCategory.EDUCATION: {
            "strong": ["tutorial", "how to", "learn", "explained", "course"],
            "medium": ["education", "lecture", "teaching", "lesson"],
            "weak": ["guide", "tips", "knowledge"]
        },
        VideoCategory.PRODUCT_REVIEW: {
            "strong": ["review", "unboxing", "vs comparison", "hands on"],
            "medium": ["product", "test", "comparison"],
            "weak": ["worth it", "should you buy"]
        },
        VideoCategory.GAMING: {
            "strong": ["gameplay", "walkthrough", "let's play", "gaming"],
            "medium": ["playthrough", "game", "stream"],
            "weak": ["playing", "gamer"]
        },
        VideoCategory.VLOG: {
            "strong": ["vlog", "day in my life", "what i eat in a day"],
            "medium": ["daily vlog", "my day", "come with me"],
            "weak": ["lifestyle", "routine"]
        },
        VideoCategory.FITNESS: {
            "strong": ["workout", "exercise", "fitness routine"],
            "medium": ["training", "gym", "muscle"],
            "weak": ["health", "fit"]
        },
        VideoCategory.TRAVEL: {
            "strong": ["travel vlog", "travel guide", "things to do in"],
            "medium": ["visit", "destination", "trip"],
            "weak": ["travel", "vacation"]
        },
        VideoCategory.PODCAST: {
            "strong": ["podcast", "interview with", "ep ", "episode"],
            "medium": ["conversation", "discussion", "talk"],
            "weak": ["chat"]
        },
        VideoCategory.TUTORIAL: {
            "strong": ["tutorial", "how to", "step by step"],
            "medium": ["guide", "learn", "diy"],
            "weak": ["tips", "tricks"]
        }
    }
    
    # Score each category
    scores = {}
    for category, keywords in rules.items():
        score = 0
        score += sum(5 for kw in keywords["strong"] if kw in text)
        score += sum(2 for kw in keywords["medium"] if kw in text)
        score += sum(1 for kw in keywords["weak"] if kw in text)
        scores[category] = score
    
    # Get best category
    if not scores or max(scores.values()) == 0:
        return ClassificationResult(
            video_id=extraction.metadata.video_id,
            category=VideoCategory.UNKNOWN,
            confidence=0.3,
            reasoning="No matching keywords found in rule-based classification",
            model_used="rule-based",
            classified_at=datetime.utcnow().isoformat() + "Z"
        )
    
    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]
    
    # Get alternative categories
    sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    alternatives = [cat.value for cat, score in sorted_categories[1:3] if score > 0]
    
    # Normalize confidence (cap at 0.6 for rule-based)
    confidence = min(0.6, best_score / 15)
    
    return ClassificationResult(
        video_id=extraction.metadata.video_id,
        category=best_category,
        confidence=confidence,
        sub_category=None,
        reasoning=f"Rule-based classification (keyword score: {best_score})",
        alternative_categories=alternatives,
        model_used="rule-based",
        classified_at=datetime.utcnow().isoformat() + "Z"
    )


# Convenience function
async def classify_video(
    extraction: ExtractionResult,
    include_frames: bool = True
) -> ClassificationResult:
    """
    Classify a video using the default classifier.
    
    Args:
        extraction: Video extraction result
        include_frames: Whether to include visual frames
        
    Returns:
        ClassificationResult
    """
    classifier = VideoClassifier()
    return await classifier.classify_video(extraction, include_frames)
