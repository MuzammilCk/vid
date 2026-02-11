"""
Default processor for general video analysis.

This processor uses Google Gemini to analyze videos that don't match
specific categories, providing a general summary, key points, and sentiment.
"""

import os
import json
import re
import google.generativeai as genai

from .base_processor import BaseProcessor
from models.schemas import ExtractionResult
from config.gemini_models import GeminiModel, RecommendedModels

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


class DefaultProcessor(BaseProcessor):
    """
    General-purpose video processor using Gemini AI.
    
    Analyzes any video type and returns a summary, key points,
    topics, and sentiment analysis.
    """
    
    def __init__(self):
        """Initialize the default processor with Gemini model."""
        if not GOOGLE_API_KEY:
            print("Warning: GOOGLE_API_KEY not set. DefaultProcessor will return minimal data.")
            self.model = None
        else:
            # Use recommended model from config
            try:
                self.model = genai.GenerativeModel(
                    model_name=RecommendedModels.DEFAULT_PROCESSOR.value,
                    generation_config={
                        "temperature": 0.3,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    }
                )
                print(f"✓ Using model: {RecommendedModels.DEFAULT_PROCESSOR.value}")
            except Exception as e:
                print(f"Warning: Could not initialize Gemini model: {e}")
                self.model = None
    
    async def process(self, extraction: ExtractionResult) -> dict:
        """
        Process video extraction and return general analysis.
        
        Args:
            extraction: Video extraction result from Phase 1
            
        Returns:
            dict: General analysis with structure:
                {
                    "type": "general",
                    "summary": str,
                    "key_points": list[str],
                    "topics": list[str],
                    "sentiment": str,
                    "transcript": str
                }
        """
        # Get text content
        text_content = self.get_text_content(extraction)
        
        # If no Gemini API, return minimal valid response
        if not self.model:
            return self._minimal_response(text_content)
        
        # Build prompt for Gemini
        prompt = self._build_prompt(extraction, text_content)
        
        try:
            # Call Gemini API (blocking call)
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            result = self._parse_response(response.text, text_content)
            return result
            
        except Exception as e:
            print(f"Error in DefaultProcessor: {e}")
            return self._minimal_response(text_content)
    
    def _build_prompt(self, extraction: ExtractionResult, text_content: str) -> str:
        """
        Build the analysis prompt for Gemini.
        
        Args:
            extraction: Video extraction result
            text_content: Full text content from video
            
        Returns:
            str: Formatted prompt for Gemini
        """
        # Truncate text to first 5000 characters
        truncated_text = text_content[:5000] if text_content else "No transcript available"
        
        prompt = f"""You are analyzing a YouTube video. Provide a comprehensive analysis and return ONLY valid JSON.

Video Information:
- Title: {extraction.metadata.title}
- Channel: {extraction.metadata.channel_name}
- Duration: {extraction.metadata.duration_seconds} seconds
- Views: {extraction.metadata.view_count:,}

Content:
{truncated_text}

Analyze this video and return ONLY valid JSON in this exact format:
{{
  "type": "general",
  "summary": "A 3-4 sentence summary of the video's main content and purpose",
  "key_points": ["main point 1", "main point 2", "main point 3"],
  "topics": ["topic1", "topic2", "topic3"],
  "sentiment": "positive" or "negative" or "neutral",
  "transcript": "the full transcript text"
}}

Rules:
- summary: Must be 3-4 complete sentences
- key_points: List 3-5 main takeaways
- topics: List 2-5 main topics/themes
- sentiment: Must be exactly "positive", "negative", or "neutral"
- transcript: Include the full text content provided above

Return ONLY the JSON object, no markdown formatting, no code blocks."""
        
        return prompt
    
    def _parse_response(self, response_text: str, original_text: str) -> dict:
        """
        Parse Gemini's JSON response.
        
        Args:
            response_text: Raw response from Gemini
            original_text: Original transcript for fallback
            
        Returns:
            dict: Parsed and validated response
        """
        try:
            # Clean up markdown code blocks if present
            cleaned = response_text.strip()
            
            # Remove ```json and ``` markers
            cleaned = re.sub(r'^```json\s*', '', cleaned)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            cleaned = cleaned.strip()
            
            # Parse JSON
            result = json.loads(cleaned)
            
            # Validate required fields
            if not isinstance(result.get("type"), str):
                result["type"] = "general"
            
            if not isinstance(result.get("summary"), str):
                result["summary"] = "Summary unavailable"
            
            if not isinstance(result.get("key_points"), list):
                result["key_points"] = []
            
            if not isinstance(result.get("topics"), list):
                result["topics"] = []
            
            if result.get("sentiment") not in ["positive", "negative", "neutral"]:
                result["sentiment"] = "neutral"
            
            if not isinstance(result.get("transcript"), str):
                result["transcript"] = original_text
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:200]}...")
            return self._minimal_response(original_text)
        
        except Exception as e:
            print(f"Unexpected error parsing response: {e}")
            return self._minimal_response(original_text)
    
    def _minimal_response(self, text_content: str) -> dict:
        """
        Return minimal valid response when Gemini fails or is unavailable.
        
        Args:
            text_content: Original text content
            
        Returns:
            dict: Minimal valid response structure
        """
        return {
            "type": "general",
            "summary": "Summary unavailable - AI processing failed or API key not configured",
            "key_points": [],
            "topics": [],
            "sentiment": "neutral",
            "transcript": text_content
        }
