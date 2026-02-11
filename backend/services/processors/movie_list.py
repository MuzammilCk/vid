"""
Movie list processor for "Top Movies" type videos.

Part 1: Extract movie titles from transcript using Gemini.
Part 2: Enrich with TMDB API data (to be implemented).
"""

import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

from config.gemini_models import RecommendedModels

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


async def extract_movies_from_transcript(
    transcript: str,
    video_title: str
) -> list[dict]:
    """
    Extract all movies mentioned in a video transcript.
    
    Uses Gemini AI to identify and extract movie titles in order,
    along with release years if mentioned.
    
    Args:
        transcript: Video transcript or captions
        video_title: Video title for context
        
    Returns:
        List of dicts: [{"title": "Movie Name", "year": 2024, "rank": 1}, ...]
        Returns empty list if extraction fails or no movies found.
    """
    if not GOOGLE_API_KEY:
        print("Warning: GOOGLE_API_KEY not set. Cannot extract movies.")
        return []
    
    if not transcript or not transcript.strip():
        print("Warning: No transcript provided for movie extraction.")
        return []
    
    try:
        # Initialize Gemini model for precise extraction
        model = genai.GenerativeModel(
            model_name=RecommendedModels.LIST_PROCESSOR.value,
            generation_config={
                "temperature": 0.1,  # Very low for precise extraction
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        # Build extraction prompt
        prompt = _build_extraction_prompt(transcript, video_title)
        
        # Call Gemini API
        response = model.generate_content(prompt)
        
        # Parse response
        movies = _parse_movie_response(response.text)
        
        # Add rank field
        for i, movie in enumerate(movies, 1):
            movie["rank"] = i
        
        # Limit to 50 movies max
        return movies[:50]
        
    except Exception as e:
        print(f"Error extracting movies: {e}")
        return []


def _build_extraction_prompt(transcript: str, video_title: str) -> str:
    """
    Build the movie extraction prompt for Gemini.
    
    Args:
        transcript: Video transcript
        video_title: Video title
        
    Returns:
        str: Formatted prompt
    """
    # Truncate transcript to 6000 chars
    truncated_transcript = transcript[:6000]
    
    prompt = f"""You are analyzing a video about movies. Extract ALL movies mentioned in order.

Video Title: {video_title}

Transcript:
{truncated_transcript}

Return a JSON array of movies with their release year if mentioned:
[
  {{"title": "Exact Movie Title", "year": 2024}},
  {{"title": "Another Movie", "year": 2023}},
  {{"title": "Movie Without Year", "year": null}}
]

CRITICAL RULES:
1. Extract movies in the EXACT order they appear in the transcript
2. Use the EXACT title mentioned in the video (don't correct or modify)
3. If release year is mentioned, include it as an integer
4. If year is NOT mentioned, use null (not a string, not 0, but null)
5. Extract ALL movies mentioned, even if it's a long list
6. Return ONLY valid JSON array, no markdown formatting, no code blocks, no explanations

JSON array:"""
    
    return prompt


def _parse_movie_response(response_text: str) -> list[dict]:
    """
    Parse Gemini's movie extraction response.
    
    Args:
        response_text: Raw response from Gemini
        
    Returns:
        list[dict]: Parsed movie list
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
        movies = json.loads(cleaned)
        
        # Validate it's a list
        if not isinstance(movies, list):
            print(f"Warning: Expected list, got {type(movies)}")
            return []
        
        # Validate each movie entry
        validated_movies = []
        for movie in movies:
            if not isinstance(movie, dict):
                continue
            
            # Must have title
            if "title" not in movie or not movie["title"]:
                continue
            
            # Ensure year is int or None
            year = movie.get("year")
            if year is not None:
                try:
                    movie["year"] = int(year) if year else None
                except (ValueError, TypeError):
                    movie["year"] = None
            
            validated_movies.append({
                "title": str(movie["title"]).strip(),
                "year": movie.get("year")
            })
        
        return validated_movies
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text[:200]}...")
        return []
    
    except Exception as e:
        print(f"Unexpected error parsing movie response: {e}")
        return []
