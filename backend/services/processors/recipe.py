"""
Recipe processor for cooking video analysis.

Extracts structured recipe data including ingredients, steps, and nutrition info.
"""

import os
import json
import re
import google.generativeai as genai

from .base_processor import BaseProcessor
from models.schemas import ExtractionResult
from config.gemini_models import RecommendedModels

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


class RecipeProcessor(BaseProcessor):
    """
    Recipe-specific video processor using Gemini AI.
    
    Extracts structured recipe data including dish name, ingredients,
    cooking steps, timing, and nutritional estimates.
    """
    
    def __init__(self):
        """Initialize the recipe processor with Gemini model."""
        if not GOOGLE_API_KEY:
            print("Warning: GOOGLE_API_KEY not set. RecipeProcessor will return minimal data.")
            self.model = None
        else:
            try:
                # Use Flash-Lite for fast structured extraction
                self.model = genai.GenerativeModel(
                    model_name=RecommendedModels.RECIPE_PROCESSOR.value,
                    generation_config={
                        "temperature": 0.2,  # Low temp for factual extraction
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 4096,  # Recipes can be long
                    }
                )
                print(f"✓ Using model: {RecommendedModels.RECIPE_PROCESSOR.value}")
            except Exception as e:
                print(f"Warning: Could not initialize Gemini model: {e}")
                self.model = None
    
    async def process(self, extraction: ExtractionResult) -> dict:
        """
        Process cooking video and extract recipe data.
        
        Args:
            extraction: Video extraction result from Phase 1
            
        Returns:
            dict: Recipe data with structure:
                {
                    "type": "recipe",
                    "dish_name": str,
                    "cuisine": str,
                    "prep_time": str,
                    "cook_time": str,
                    "servings": int,
                    "difficulty": str,
                    "ingredients": list[dict],
                    "steps": list[dict],
                    "tips": list[str],
                    "nutrition_estimate": dict
                }
        """
        # Get text content (up to 8000 chars for recipes)
        text_content = self.get_text_content(extraction)[:8000]
        
        # If no Gemini API, return minimal valid response
        if not self.model:
            return self._minimal_response(extraction.metadata.title, text_content)
        
        # Build prompt for Gemini
        prompt = self._build_prompt(extraction, text_content)
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            result = self._parse_response(response.text, extraction.metadata.title, text_content)
            return result
            
        except Exception as e:
            print(f"Error in RecipeProcessor: {e}")
            return self._minimal_response(extraction.metadata.title, text_content)
    
    def _build_prompt(self, extraction: ExtractionResult, text_content: str) -> str:
        """
        Build the recipe extraction prompt for Gemini.
        
        Args:
            extraction: Video extraction result
            text_content: Full text content from video
            
        Returns:
            str: Formatted prompt for Gemini
        """
        prompt = f"""You are analyzing a cooking/recipe video. Extract ALL recipe information and return ONLY valid JSON.

Video Information:
- Title: {extraction.metadata.title}
- Channel: {extraction.metadata.channel_name}
- Duration: {extraction.metadata.duration_seconds} seconds

Full Transcript/Captions:
{text_content if text_content else "No transcript available - video may rely on visual instructions"}

Extract the recipe and return ONLY valid JSON in this EXACT format:
{{
  "type": "recipe",
  "dish_name": "name of the dish being made",
  "cuisine": "cuisine type (e.g., Italian, Indian, Mexican, American, Asian, etc.)",
  "prep_time": "preparation time as string (e.g., '15 minutes', '30 mins')",
  "cook_time": "cooking time as string (e.g., '45 minutes', '1 hour')",
  "servings": number of servings as integer,
  "difficulty": "easy" or "medium" or "hard",
  "ingredients": [
    {{
      "item": "ingredient name",
      "quantity": "amount with unit (e.g., '2 cups', '500g', '1 tbsp')",
      "notes": "any preparation notes or alternatives (e.g., 'chopped', 'optional', 'or substitute X')"
    }}
  ],
  "steps": [
    {{
      "step": step number as integer (1, 2, 3, etc.),
      "instruction": "detailed instruction for this step",
      "timestamp": "MM:SS format if mentioned, or null"
    }}
  ],
  "tips": ["cooking tip 1", "cooking tip 2", "pro tip 3"],
  "nutrition_estimate": {{
    "calories": estimated calories per serving as integer,
    "protein": "protein amount as string (e.g., '25g')",
    "carbs": "carbs amount as string (e.g., '45g')",
    "fat": "fat amount as string (e.g., '15g')"
  }},
  "transcript_completeness": "complete" or "partial" or "visual_only"
}}

CRITICAL RULES:
1. Extract ALL ingredients mentioned, even if briefly
2. Extract ALL steps in order
3. If quantities are not mentioned, use "to taste" or "as needed"
4. If prep/cook time not mentioned, estimate based on dish complexity
5. If nutrition not mentioned, provide reasonable estimates for the dish type
6. For difficulty: easy = <30 min total, medium = 30-60 min, hard = >60 min or complex techniques
7. If transcript is incomplete or missing, set transcript_completeness to "partial" or "visual_only"
8. Include any tips, tricks, or variations mentioned
9. Return ONLY the JSON object, no markdown formatting, no code blocks

Extract the recipe now:"""
        
        return prompt
    
    def _parse_response(self, response_text: str, video_title: str, original_text: str) -> dict:
        """
        Parse Gemini's JSON response.
        
        Args:
            response_text: Raw response from Gemini
            video_title: Video title for fallback
            original_text: Original transcript for fallback
            
        Returns:
            dict: Parsed and validated recipe data
        """
        try:
            # Clean up markdown code blocks if present
            cleaned = response_text.strip()
            cleaned = re.sub(r'^```json\s*', '', cleaned)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            cleaned = cleaned.strip()
            
            # Parse JSON
            result = json.loads(cleaned)
            
            # Validate and set defaults for required fields
            result["type"] = "recipe"
            
            if not isinstance(result.get("dish_name"), str) or not result["dish_name"]:
                result["dish_name"] = video_title
            
            if not isinstance(result.get("cuisine"), str):
                result["cuisine"] = "Unknown"
            
            if not isinstance(result.get("prep_time"), str):
                result["prep_time"] = "Not specified"
            
            if not isinstance(result.get("cook_time"), str):
                result["cook_time"] = "Not specified"
            
            if not isinstance(result.get("servings"), int):
                result["servings"] = 0
            
            if result.get("difficulty") not in ["easy", "medium", "hard"]:
                result["difficulty"] = "medium"
            
            if not isinstance(result.get("ingredients"), list):
                result["ingredients"] = []
            
            if not isinstance(result.get("steps"), list):
                result["steps"] = []
            
            if not isinstance(result.get("tips"), list):
                result["tips"] = []
            
            if not isinstance(result.get("nutrition_estimate"), dict):
                result["nutrition_estimate"] = {
                    "calories": 0,
                    "protein": "Not available",
                    "carbs": "Not available",
                    "fat": "Not available"
                }
            
            if not result.get("transcript_completeness"):
                result["transcript_completeness"] = "complete" if original_text else "visual_only"
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:200]}...")
            return self._minimal_response(video_title, original_text)
        
        except Exception as e:
            print(f"Unexpected error parsing response: {e}")
            return self._minimal_response(video_title, original_text)
    
    def _minimal_response(self, video_title: str, text_content: str) -> dict:
        """
        Return minimal valid response when Gemini fails.
        
        Args:
            video_title: Video title
            text_content: Original text content
            
        Returns:
            dict: Minimal valid recipe structure
        """
        return {
            "type": "recipe",
            "dish_name": video_title,
            "cuisine": "Unknown",
            "prep_time": "Not specified",
            "cook_time": "Not specified",
            "servings": 0,
            "difficulty": "medium",
            "ingredients": [],
            "steps": [],
            "tips": [],
            "nutrition_estimate": {
                "calories": 0,
                "protein": "Not available",
                "carbs": "Not available",
                "fat": "Not available"
            },
            "transcript_completeness": "visual_only" if not text_content else "partial",
            "error": "AI processing failed or API key not configured"
        }
