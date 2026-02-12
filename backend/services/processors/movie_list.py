"""
Movie list processor for "Top Movies" type videos.

Part 1: Extract movie titles from transcript using Gemini (Multimodal support).
Part 2: Enrich with TMDB API data.
Part 3: Complete Processor Class.
"""

import os
import json
import re
import httpx
import asyncio
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

from .base_processor import BaseProcessor
from models.schemas import ExtractionResult
from config.gemini_models import RecommendedModels

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# TMDB API configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


class MovieListProcessor(BaseProcessor):
    """
    Processor for "Top Movies" style videos.
    
    Features:
    - Multimodal extraction (uses Transcript + Key Frames) to handle videos 
      with no voiceover or where visuals contain key info.
    - TMDB API enrichment for valid movie data.
    """
    
    def __init__(self):
        super().__init__()
        if not GOOGLE_API_KEY:
            print("Warning: GOOGLE_API_KEY not set. MovieListProcessor limited.")
            self.model = None
        else:
            # Use recommended model (likely Gemini 2.5 Flash for multimodal)
            self.model = genai.GenerativeModel(
                model_name=RecommendedModels.LIST_PROCESSOR.value,
                generation_config={
                    "temperature": 0.1,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 4096,
                }
            )

    async def process(self, extraction: ExtractionResult) -> dict:
        """
        Process video to extract and enrich movie list.
        
        Args:
            extraction: ExtractionResult containing transcript and key frames.
            
        Returns:
            dict: Structured movie list data.
        """
        video_title = extraction.metadata.title
        transcript = self.get_text_content(extraction)
        key_frames = extraction.key_frame_paths
        
        # Step 1: Extract movies (Multimodal)
        print(f"🎬 Extracting movies from '{video_title}'...")
        raw_movies = await self._extract_movies(transcript, video_title, key_frames)
        
        if not raw_movies:
            print("⚠️ No movies extracted from video.")
            return {
                "type": "movie_list",
                "movies": [],
                "count": 0,
                "extraction_method": "failed"
            }
            
        # Step 2: Enrich with TMDB
        print(f"🌟 Enriching {len(raw_movies)} movies with TMDB...")
        enriched_movies = []
        
        # Process in parallel chunks to avoid hitting API limits too hard but faster than serial
        # TMDB rate limits are usually generous enough for small batches
        chunk_size = 5
        for i in range(0, len(raw_movies), chunk_size):
            chunk = raw_movies[i:i+chunk_size]
            tasks = [
                enrich_movie_with_tmdb(m["title"], m.get("year")) 
                for m in chunk
            ]
            results = await asyncio.gather(*tasks)
            
            # Combine raw extraction with enrichment (fallback to raw if enrichment fails)
            for raw, enriched in zip(chunk, results):
                if enriched:
                    # Keep rank from extraction, update data from TMDB
                    enriched["rank"] = raw["rank"]
                    enriched_movies.append(enriched)
                else:
                    # Fallback to raw data if not found in TMDB
                    raw["tmdb_found"] = False
                    enriched_movies.append(raw)
                    
        return {
            "type": "movie_list",
            "movies": enriched_movies,
            "count": len(enriched_movies),
            "extraction_method": "multimodal" if key_frames else "text_only"
        }

    async def _extract_movies(self, transcript: str, video_title: str, key_frame_paths: list[str]) -> list[dict]:
        """
        Extract movies using Gemini (Multimodal).
        """
        if not self.model:
            return []

        # Prepare content parts
        content_parts = []
        
        # Add Prompt
        prompt_text = self._build_extraction_prompt(transcript, video_title, has_images=bool(key_frame_paths))
        content_parts.append(prompt_text)
        
        # Add Images (up to 10 frames to avoid token limits/latency)
        images_loaded = 0
        if key_frame_paths:
            print(f"🖼️ incorporating {len(key_frame_paths[:10])} key frames for analysis...")
            for path in key_frame_paths[:10]:
                try:
                    img = Image.open(path)
                    content_parts.append(img)
                    images_loaded += 1
                except Exception as e:
                    print(f"⚠️ Failed to load frame {path}: {e}")
        
        try:
            # Call Gemini
            response = await self.model.generate_content_async(content_parts)
            return self._parse_movie_response(response.text)
        except Exception as e:
            print(f"❌ Error in movie extraction: {e}")
            return []

    def _build_extraction_prompt(self, transcript: str, video_title: str, has_images: bool) -> str:
        """Build multimodal prompt."""
        truncated_transcript = transcript[:6000] if transcript else "No transcript available."
        
        visual_instruction = ""
        if has_images:
            visual_instruction = """
IMPORTANT: 
- Use BOTH the transcript AND the provided video frames.
- If the video is a montage with no voiceover, extract movie titles visible on screen (text overlays, title cards).
- Visual cues are as important as spoken text.
"""

        return f"""You are analyzing a "Top Movies" video. Extract ALL movies mentioned.

Video Title: {video_title}
{visual_instruction}

Transcript:
{truncated_transcript}

Return a JSON array of movies in order. Format:
[
  {{"title": "Exact Movie Title", "year": 2024}},
  {{"title": "Another Movie", "year": null}}
]

RULES:
1. Extract exact titles.
2. Include year if mentioned (spoken or on screen) or inferable from context.
3. Order by appearance/ranking (usually countdown 10 to 1).
4. Return ONLY valid JSON.
"""

    def _parse_movie_response(self, response_text: str) -> list[dict]:
        """Reuse existing parsing logic."""
        # This duplicates the existing standalone function logic but keeps class self-contained
        # For simplicity, we can call the standalone function if we kept it, 
        # but better to have it here as method or static method.
        # Let's use the code from the standalone function directly here.
        try:
            cleaned = response_text.strip()
            cleaned = re.sub(r'^```json\s*', '', cleaned)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            cleaned = cleaned.strip()
            
            movies = json.loads(cleaned)
            if not isinstance(movies, list): return []
            
            validated = []
            for i, m in enumerate(movies, 1):
                if not isinstance(m, dict) or "title" not in m: continue
                # Validate year
                year = m.get("year")
                try:
                    year = int(year) if year is not None else None
                except:
                    year = None
                
                validated.append({
                    "title": str(m["title"]).strip(),
                    "year": year,
                    "rank": i # Assign rank based on extraction order (usually reliable)
                })
            return validated
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            return []

# ============================================================================
# Helpers & Standalone Functions (kept for backward compatibility/testing)
# ============================================================================

# We keep the standalone extraction function for the existing test script compatibility
# but simply redirect it to use the class logic could be cleaner, 
# OR we just leave the standalone functions as helpers.

async def extract_movies_from_transcript(transcript: str, video_title: str) -> list[dict]:
    """Legacy/Testing standalone function."""
    processor = MovieListProcessor()
    # Mock result with no frames
    from models.schemas import ExtractionResult, VideoMetadata
    mock_meta = VideoMetadata(
        video_id="test", title=video_title, description="", 
        channel_name="", channel_id="", duration_seconds=0, 
        thumbnail_url="", published_at="", category_id=""
    )
    mock_extraction = ExtractionResult(
        metadata=mock_meta,
        transcript=transcript,
        key_frame_paths=[]
    )
    # Use private method for direct extraction test
    return await processor._extract_movies(transcript, video_title, [])


def get_director_from_credits(credits: dict) -> str | None:
    """Extract director name from TMDB credits."""
    crew = credits.get("crew", [])
    directors = [person["name"] for person in crew if person.get("job") == "Director"]
    return directors[0] if directors else None


async def enrich_movie_with_tmdb(movie_title: str, year: int | None = None) -> dict | None:
    """
    Fetch movie data from TMDB API.
    """
    if not TMDB_API_KEY:
        print("Warning: TMDB_API_KEY not set.")
        return None
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Search
            search_url = "https://api.themoviedb.org/3/search/movie"
            params = {"api_key": TMDB_API_KEY, "query": movie_title}
            if year: params["year"] = year
            
            resp = await client.get(search_url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
            if not data.get("results"): return None
            
            movie = data["results"][0]
            movie_id = movie["id"]
            
            # Details
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            details_params = {"api_key": TMDB_API_KEY, "append_to_response": "credits"}
            details_resp = await client.get(details_url, params=details_params)
            details = details_resp.json()
            
            # Providers
            prov_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
            prov_resp = await client.get(prov_url, params={"api_key": TMDB_API_KEY})
            prov_data = prov_resp.json()
            us_prov = prov_data.get("results", {}).get("US", {})
            
            return {
                "title": details.get("title", movie_title),
                "year": details["release_date"][:4] if details.get("release_date") else None,
                "tmdb_id": movie_id,
                "tmdb_rating": details.get("vote_average", 0),
                "genres": [g["name"] for g in details.get("genres", [])],
                "overview": details.get("overview", ""),
                "poster_url": f"https://image.tmdb.org/t/p/w500{details['poster_path']}" if details.get("poster_path") else None,
                "runtime": details.get("runtime"),
                "director": get_director_from_credits(details.get("credits", {})),
                "streaming": {
                    "flatrate": [p["provider_name"] for p in us_prov.get("flatrate", [])],
                    "rent": [p["provider_name"] for p in us_prov.get("rent", [])],
                    "buy": [p["provider_name"] for p in us_prov.get("buy", [])]
                }
            }
    except Exception as e:
        print(f"Error enriching {movie_title}: {e}")
        return None
