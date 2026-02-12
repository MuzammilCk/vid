# 🛡️ PHASE 3 IMPLEMENTATION GUIDE
## *Anti-Hallucination Strategy for Category Processors*

---

## 🎯 GOLDEN RULES FOR PHASE 3

```
1. Build ONE processor at a time (not all at once)
2. Test EACH processor with a real video before moving to next
3. Verify ALL API endpoints against official docs BEFORE coding
4. Use MOCK data first, then swap to real APIs
5. Never let AI generate API responses - verify them yourself
6. Commit after EACH working processor
```

---

## 📊 BUILD ORDER (Start → Finish)

```
BUILD IN THIS EXACT ORDER:

1. Base Processor (abstract class) ✅ COMPLETE
2. Default Processor (simplest) ✅ COMPLETE
3. Recipe Processor (no external API) ⏳ NEXT
4. Comedy Processor ✅ SAFE (no external API)
5. Education Processor ✅ SAFE (no external API)
6. Movie List Processor ⚠️ MEDIUM (TMDB API)
7. Song List Processor ⚠️ MEDIUM (Spotify API)
8. Processor Router (connects everything) ✅ SAFE

WHY THIS ORDER:
- Start with simple ones (no external APIs)
- Build confidence before tackling TMDB/Spotify
- Test the whole pipeline early with Default processor
```

---

## ✅ STEP 1: BASE PROCESSOR (COMPLETE)

### **Prompt to Use:**
```
CONTEXT: Building VidBrain AI Phase 3
TECH: Python, FastAPI, Pydantic
FILE: backend/services/processors/base_processor.py

Create an abstract base class called BaseProcessor with:
1. An abstract method: async def process(self, extraction: ExtractionResult) -> dict
2. A helper method: def get_text_content(self, extraction: ExtractionResult) -> str
   - Returns extraction.captions if available
   - Else returns extraction.transcript
   - Else returns extraction.metadata.description
   - Else returns empty string

Use Python's abc module for the abstract class.
Import ExtractionResult from models.schemas.
Add proper type hints and docstrings.
```

### **Expected Output:**
```python
from abc import ABC, abstractmethod
from models.schemas import ExtractionResult

class BaseProcessor(ABC):
    """Base class for all category-specific processors."""
    
    @abstractmethod
    async def process(self, extraction: ExtractionResult) -> dict:
        """Process extraction and return structured output."""
        pass
    
    def get_text_content(self, extraction: ExtractionResult) -> str:
        """Get the best available text content from the video."""
        return (
            extraction.captions
            or extraction.transcript
            or extraction.metadata.description
            or ""
        )
```

### **Verification:**
```bash
cd backend
python -c "from services.processors.base_processor import BaseProcessor; print('✅ Import works')"
```

---

## ✅ STEP 2: DEFAULT PROCESSOR (COMPLETE)

### **Implementation Summary:**
✅ **Created**: `backend/services/processors/default.py`  
✅ **Test File**: `backend/test_default.py`  
✅ **Model Used**: `gemini-2.5-flash` (via `RecommendedModels.DEFAULT_PROCESSOR`)  
✅ **Status**: Working and tested successfully

### **Test Results:**
```
✅ Type: general
✅ Summary: 4-sentence summary generated
✅ Key Points: 4 points extracted
✅ Topics: Community event, Competition, Prize money, Tamil Nadu interaction
✅ Sentiment: positive
✅ Transcript length: 98 characters
✅ ALL TESTS PASSED!
```

### **Key Features Implemented:**
1. ✅ Inherits from BaseProcessor
2. ✅ Uses Gemini 2.5 Flash (stable model)
3. ✅ Returns structured JSON with summary, key_points, topics, sentiment
4. ✅ Handles JSON parsing with regex cleanup
5. ✅ Fallback to minimal response on errors
6. ✅ Truncates text to 5000 chars for API efficiency

### **Files Created:**
- `backend/services/processors/default.py` - Main processor
- `backend/test_default.py` - Test script
- `backend/config/gemini_models.py` - Centralized model configuration

### **Why Start Here:**
- No external APIs needed
- Pure AI processing with Gemini
- Tests the base architecture
- Will be used for unknown categories

### **Prompt Used (for reference):**
```
CONTEXT: Building VidBrain AI Phase 3
TECH: Python, Google Gemini API
FILE: backend/services/processors/default.py

{{ ... }}
```

### **Prompt to Use:**
```
CONTEXT: Building VidBrain AI Phase 3
TECH: Python, Google Gemini API
FILE: backend/services/processors/default.py

Create DefaultProcessor class that:
1. Inherits from BaseProcessor
2. Implements async def process(self, extraction: ExtractionResult) -> dict
3. Uses Google Gemini to analyze the video and return:
   {
     "type": "general",
     "summary": "3-4 sentence summary",
     "key_points": ["point 1", "point 2", "point 3"],
     "topics": ["topic1", "topic2"],
     "sentiment": "positive" or "negative" or "neutral",
     "transcript": "full transcript or captions"
   }

Use the same Gemini setup from classifier.py:
- Import genai from google.generativeai
- Use gemini-2.0-flash-exp model
- Temperature 0.3 for this task
- Send: video title, description, and first 5000 chars of transcript
- Ask Gemini to return valid JSON only

Handle: API errors, invalid JSON responses.
Parse response with json.loads() and regex cleanup for ```json blocks.
```

### **Test Before Moving On:**

Create `backend/test_default_processor.py`:
```python
import asyncio
from services.youtube_extractor import extract_all
from services.processors.default import DefaultProcessor

async def test():
    # Use a simple, short video
    extraction = await extract_all("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    processor = DefaultProcessor()
    result = await processor.process(extraction)
    
    print("\n✅ Default Processor Result:")
    print(f"Type: {result['type']}")
    print(f"Summary: {result['summary'][:100]}...")
    print(f"Key Points: {len(result['key_points'])}")
    print(f"Topics: {result['topics']}")
    print(f"Sentiment: {result['sentiment']}")
    
    assert result['type'] == 'general'
    assert 'summary' in result
    assert len(result['key_points']) > 0
    print("\n✅ All assertions passed!")

asyncio.run(test())
```

Run: `python test_default_processor.py`

**✅ STEP 2 COMPLETE** - Tested with real YouTube video on 2026-02-12

**Git Commit**: `git commit -m "Phase 3: Default processor working with gemini-2.5-flash"`

---

## 🏗️ STEP 3: RECIPE PROCESSOR (20 minutes)

### **Why This One Next:**
- No external APIs
- Clear structured output
- Good practice for prompt engineering

### **Prompt Template:**
```
CONTEXT: Building VidBrain AI Phase 3
TECH: Python, Google Gemini API
FILE: backend/services/processors/recipe.py

Create RecipeProcessor class that:
1. Inherits from BaseProcessor
2. Implements async def process(self, extraction: ExtractionResult) -> dict
3. Sends transcript to Gemini with this EXACT prompt:

"You are analyzing a cooking/recipe video. Extract the following information and return as valid JSON:

{
  "type": "recipe",
  "dish_name": "name of the dish",
  "cuisine": "cuisine type (Italian, Indian, etc.)",
  "prep_time": "preparation time",
  "cook_time": "cooking time",
  "servings": number,
  "difficulty": "easy/medium/hard",
  "ingredients": [
    {"item": "ingredient name", "quantity": "amount", "notes": "any notes"}
  ],
  "steps": [
    {"step": 1, "instruction": "step description", "timestamp": "MM:SS or null"}
  ],
  "tips": ["tip 1", "tip 2"],
  "nutrition_estimate": {
    "calories": estimated number,
    "protein": "amount",
    "carbs": "amount",
    "fat": "amount"
  }
}

Video Title: {title}
Transcript: {transcript}

Return ONLY valid JSON, no markdown, no code blocks."

4. Parse and validate the JSON response
5. Return the structured dict

Use gemini-2.0-flash-exp model, temperature 0.2.
Handle: missing ingredients, no timestamps in transcript, API errors.
If parsing fails, return a minimal valid structure with error noted.
```

### **Test File:** `backend/test_recipe_processor.py`
```python
import asyncio
from services.youtube_extractor import extract_all
from services.processors.recipe import RecipeProcessor

async def test():
    # Find a real recipe video on YouTube
    # Example: "https://www.youtube.com/watch?v=..." (search "simple pasta recipe")
    test_url = input("Enter a recipe video URL: ")
    
    extraction = await extract_all(test_url)
    processor = RecipeProcessor()
    result = await processor.process(extraction)
    
    print("\n✅ Recipe Processor Result:")
    print(f"Dish: {result['dish_name']}")
    print(f"Cuisine: {result['cuisine']}")
    print(f"Ingredients: {len(result['ingredients'])}")
    print(f"Steps: {len(result['steps'])}")
    print(f"Difficulty: {result['difficulty']}")
    
    assert result['type'] == 'recipe'
    assert 'dish_name' in result
    assert len(result['ingredients']) > 0
    print("\n✅ Recipe processor test passed!")

asyncio.run(test())
```

**✅ COMMIT:** `git commit -m "Phase 3: Recipe processor working"`

---

## 🏗️ STEP 4: COMEDY PROCESSOR (20 minutes)

### **Prompt Template:**
```
CONTEXT: Building VidBrain AI Phase 3
TECH: Python, Google Gemini API
FILE: backend/services/processors/comedy.py

Create ComedyProcessor that analyzes comedy videos and returns:

{
  "type": "comedy",
  "title": "video title",
  "performer": "comedian/performer name",
  "comedy_style": "standup/skit/improv/roast/parody",
  "script": "formatted transcript",
  "best_moments": [
    {"timestamp": "MM:SS", "description": "what happens", "laugh_score": 1-10}
  ],
  "shareable_quotes": ["funny quote 1", "funny quote 2"],
  "humor_rating": 1-10,
  "themes": ["theme1", "theme2"]
}

Use Gemini to analyze the transcript and identify funny moments.
Handle: no clear punchlines, non-English comedy, timestamps not available.
Temperature: 0.4 (slightly more creative for comedy analysis)
```

**✅ COMMIT:** `git commit -m "Phase 3: Comedy processor working"`

---

## 🏗️ STEP 5: EDUCATION PROCESSOR (25 minutes)

### **Prompt Template:**
```
CONTEXT: Building VidBrain AI Phase 3
TECH: Python, Google Gemini API
FILE: backend/services/processors/education.py

Create EducationProcessor that creates study materials:

{
  "type": "education",
  "topic": "main topic",
  "subject_area": "field (Science, Math, History, etc.)",
  "difficulty_level": "beginner/intermediate/advanced",
  "summary": "TL;DW summary",
  "key_concepts": [
    {"concept": "name", "definition": "explanation", "timestamp": "MM:SS or null"}
  ],
  "study_notes": "# Markdown formatted notes\n## Section 1\n...",
  "timestamps": [
    {"time": "MM:SS", "topic": "what's being discussed"}
  ],
  "quiz": [
    {
      "question": "question text",
      "options": ["A", "B", "C", "D"],
      "correct": "B",
      "explanation": "why this is correct"
    }
  ]
}

Generate 5-10 quiz questions based on the content.
Format study notes in clean Markdown.
Temperature: 0.2 (factual content)
```

**✅ COMMIT:** `git commit -m "Phase 3: Education processor working"`

---

## 🏗️ STEP 6: MOVIE LIST PROCESSOR (45 minutes) ⚠️

### **⚠️ CRITICAL: VERIFY TMDB API FIRST**

**Before writing ANY code:**

1. **Get TMDB API Key:**
   - Go to https://www.themoviedb.org/settings/api
   - Copy your API key
   - Add to `.env`: `TMDB_API_KEY=your_key_here`

2. **Test TMDB API manually:**

Create `backend/test_tmdb_api.py`:
```python
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_tmdb():
    api_key = os.getenv("TMDB_API_KEY")
    
    # Test 1: Search for a movie
    print("\n1. Testing movie search...")
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {"api_key": api_key, "query": "Dune Part Two", "year": 2024}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        if data.get("results"):
            movie = data["results"][0]
            movie_id = movie["id"]
            print(f"✅ Found: {movie['title']} (ID: {movie_id})")
            
            # Test 2: Get movie details
            print("\n2. Testing movie details...")
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            details_response = await client.get(details_url, params={"api_key": api_key})
            details = details_response.json()
            print(f"✅ Rating: {details['vote_average']}")
            print(f"✅ Poster: https://image.tmdb.org/t/p/w500{details['poster_path']}")
            
            # Test 3: Get watch providers
            print("\n3. Testing watch providers...")
            providers_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
            providers_response = await client.get(providers_url, params={"api_key": api_key})
            providers_data = providers_response.json()
            
            us_providers = providers_data.get("results", {}).get("US", {})
            print(f"✅ Streaming: {us_providers.get('flatrate', [])}")
            print(f"✅ Rent: {us_providers.get('rent', [])}")
            
            print("\n✅ TMDB API is working correctly!")
        else:
            print("❌ No results found. Check your API key.")

import asyncio
asyncio.run(test_tmdb())
```

Run: `python test_tmdb_api.py`

**Only proceed if all 3 tests pass!**

### **Now Build the Processor:**

**Step 6A: Extract Movies with Gemini (15 min)**

```
PROMPT:
Create a function extract_movies_from_transcript(transcript: str, title: str) -> list[dict]

Use Gemini to extract movie titles from the transcript.
Prompt: "Extract ALL movies mentioned in this video. Return JSON array:
[{\"title\": \"Movie Name\", \"year\": 2024}]

Video Title: {title}
Transcript: {transcript}

Return ONLY valid JSON."

Return format: [{"title": "Dune: Part Two", "year": 2024}, ...]
Handle: no movies found (return empty list), invalid JSON.
```

**Step 6B: Enrich with TMDB (20 min)**

```
PROMPT:
Create a function enrich_movie_with_tmdb(movie_title: str, year: int) -> dict

Use httpx to call TMDB API:
1. Search: GET https://api.themoviedb.org/3/search/movie?api_key={key}&query={title}&year={year}
2. Get first result's ID
3. Get details: GET https://api.themoviedb.org/3/movie/{id}?api_key={key}
4. Get providers: GET https://api.themoviedb.org/3/movie/{id}/watch/providers?api_key={key}

Return:
{
  "title": str,
  "year": int,
  "tmdb_id": int,
  "tmdb_rating": float,
  "genres": list[str],
  "overview": str,
  "poster_url": str,  # https://image.tmdb.org/t/p/w500{poster_path}
  "runtime": int,
  "director": str or None,
  "streaming": {
    "flatrate": list[str],  # From results.US.flatrate[].provider_name
    "rent": list[str],
    "buy": list[str]
  }
}

Handle: movie not found (return None), no streaming data (empty arrays).
Use TMDB_API_KEY from os.getenv().
```

**Step 6C: Combine into MovieListProcessor (10 min)**

```python
class MovieListProcessor(BaseProcessor):
    async def process(self, extraction: ExtractionResult) -> dict:
        # 1. Extract movies from transcript
        text = self.get_text_content(extraction)
        movies_raw = await extract_movies_from_transcript(text, extraction.metadata.title)
        
        # 2. Enrich each movie
        enriched_movies = []
        for i, movie in enumerate(movies_raw[:20]):  # Limit to 20
            enriched = await enrich_movie_with_tmdb(movie["title"], movie.get("year"))
            if enriched:
                enriched["rank"] = i + 1
                enriched_movies.append(enriched)
        
        # 3. Return structured output
        return {
            "type": "movie_list",
            "title": extraction.metadata.title,
            "total_movies": len(enriched_movies),
            "movies": enriched_movies
        }
```

**✅ COMMIT:** `git commit -m "Phase 3: Movie list processor with TMDB"`

---

## 🏗️ STEP 7: SONG LIST PROCESSOR (45 minutes) ⚠️

### **⚠️ CRITICAL: VERIFY SPOTIFY API FIRST**

**Before writing code:**

1. **Get Spotify Credentials:**
   - Go to https://developer.spotify.com/dashboard
   - Create an app
   - Copy Client ID and Client Secret
   - Add to `.env`:
     ```
     SPOTIFY_CLIENT_ID=your_client_id
     SPOTIFY_CLIENT_SECRET=your_client_secret
     ```

2. **Test Spotify API:**

Create `backend/test_spotify_api.py`:
```python
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

def test_spotify():
    # Setup
    auth_manager = SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Test search
    print("\n1. Testing song search...")
    results = sp.search(q="track:Espresso artist:Sabrina Carpenter", type="track", limit=1)
    
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        print(f"✅ Found: {track['name']} by {track['artists'][0]['name']}")
        print(f"✅ Spotify ID: {track['id']}")
        print(f"✅ Album Art: {track['album']['images'][0]['url']}")
        print(f"✅ Preview URL: {track['preview_url']}")
        print(f"✅ Popularity: {track['popularity']}")
        print("\n✅ Spotify API is working!")
    else:
        print("❌ No results. Check your credentials.")

test_spotify()
```

Run: `python test_spotify_api.py`

### **Build the Processor:**

```
PROMPT:
Create SongListProcessor similar to MovieListProcessor:

1. Extract songs from transcript using Gemini:
   Return: [{"title": "song name", "artist": "artist name"}, ...]

2. Enrich with Spotify using spotipy:
   sp.search(q=f"track:{title} artist:{artist}", type="track", limit=1)
   
   Extract:
   - spotify_id
   - spotify_url: track['external_urls']['spotify']
   - preview_url: track['preview_url']
   - album_art: track['album']['images'][0]['url']
   - popularity: track['popularity']
   - duration_ms: track['duration_ms']
   - album: track['album']['name']

3. Return:
   {
     "type": "song_list",
     "title": video title,
     "total_songs": count,
     "songs": [enriched songs with rank],
     "playlist_ready": true if songs > 0
   }

Handle: song not found on Spotify (skip it), no preview available (null).
```

**✅ COMMIT:** `git commit -m "Phase 3: Song list processor with Spotify"`

---

## 🏗️ STEP 8: PROCESSOR ROUTER (10 minutes)

### **Create the Router:**

`backend/services/processors/__init__.py`:

```python
"""
Category-specific processor router.
Maps video categories to their specialized processors.
"""

from models.schemas import VideoCategory, ExtractionResult
from .base_processor import BaseProcessor
from .default import DefaultProcessor
from .movie_list import MovieListProcessor
from .song_list import SongListProcessor
from .recipe import RecipeProcessor
from .comedy import ComedyProcessor
from .education import EducationProcessor

# Processor registry
PROCESSOR_MAP = {
    VideoCategory.MOVIE_LIST: MovieListProcessor(),
    VideoCategory.SONG_LIST: SongListProcessor(),
    VideoCategory.RECIPE: RecipeProcessor(),
    VideoCategory.COMEDY: ComedyProcessor(),
    VideoCategory.EDUCATION: EducationProcessor(),
    # Add more as you build them
}

async def process_video(
    category: VideoCategory,
    extraction: ExtractionResult
) -> dict:
    """
    Route extraction to the appropriate processor based on category.
    
    Args:
        category: Detected video category
        extraction: Video extraction result
        
    Returns:
        dict: Structured processor output
    """
    processor = PROCESSOR_MAP.get(category, DefaultProcessor())
    return await processor.process(extraction)


# Export for easy importing
__all__ = [
    'process_video',
    'BaseProcessor',
    'DefaultProcessor',
    'MovieListProcessor',
    'SongListProcessor',
    'RecipeProcessor',
    'ComedyProcessor',
    'EducationProcessor'
]
```

### **Test the Router:**

`backend/test_processor_router.py`:
```python
import asyncio
from models.schemas import VideoCategory
from services.youtube_extractor import extract_all
from services.processors import process_video

async def test():
    # Test with different video types
    tests = [
        ("https://www.youtube.com/watch?v=...", VideoCategory.RECIPE),  # Recipe video
        # Add more test cases
    ]
    
    for url, expected_category in tests:
        print(f"\n{'='*60}")
        print(f"Testing: {expected_category.value}")
        print(f"{'='*60}")
        
        extraction = await extract_all(url)
        result = await process_video(expected_category, extraction)
        
        print(f"✅ Type: {result['type']}")
        print(f"✅ Keys: {list(result.keys())}")
        
        assert result['type'] == expected_category.value
        print("✅ Test passed!")

asyncio.run(test())
```

**✅ COMMIT:** `git commit -m "Phase 3: Processor router complete"`

---

## 🏗️ STEP 9: INTEGRATE INTO ANALYZE ENDPOINT

### **Update `backend/routers/analyze.py`:**

```python
# Add import
from services.processors import process_video

# In analyze_video function, after classification:

# Step 3: Process with category-specific processor
print(f"\n{'='*60}")
print(f"Job {job_id}: Processing as {classification_result.category.value}")
print(f"{'='*60}\n")

processed_result = await process_video(
    classification_result.category,
    extraction_result
)

# Update response to include processed result
return AnalyzeResponse(
    job_id=job_id,
    status=JobStatus.COMPLETED,
    category=classification_result.category,
    metadata=extraction_result.metadata,
    result=extraction_result,
    processed_output=processed_result,  # NEW!
    error=None
)
```

### **Update schemas.py:**

```python
class AnalyzeResponse(BaseModel):
    job_id: str
    status: JobStatus
    category: Optional[VideoCategory] = None
    metadata: Optional[VideoMetadata] = None
    result: Optional[ExtractionResult] = None
    processed_output: Optional[dict] = None  # NEW!
    error: Optional[str] = None
```

**✅ COMMIT:** `git commit -m "Phase 3: Processors integrated into analyze endpoint"`

---

## ✅ PHASE 3 FINAL CHECKLIST

```
PROCESSORS BUILT:
□ Base Processor (abstract class)
□ Default Processor (general purpose)
□ Recipe Processor (AI-only, no external API)
□ Comedy Processor (AI-only, no external API)
□ Education Processor (AI-only, no external API)
□ Movie List Processor (with TMDB API)
□ Song List Processor (with Spotify API)

TESTING:
□ Each processor tested individually
□ Router tested with multiple categories
□ Integrated into analyze endpoint
□ End-to-end test with real videos

API VERIFICATION:
□ TMDB API key working
□ Spotify credentials working
□ All endpoints verified against docs
□ Error handling for API failures

CODE QUALITY:
□ All processors inherit from BaseProcessor
□ Proper async/await usage
□ Error handling in place
□ Type hints on all functions
□ Docstrings added
```

---

## 🚨 ANTI-HALLUCINATION CHECKLIST

Before accepting ANY code from AI:

```
□ Did you verify the API endpoint exists in official docs?
□ Did you test the API manually first?
□ Is the response format what the docs say?
□ Does the code have proper error handling?
□ Did you test it with a real video?
□ Does it return the expected structure?
```

---

## 🎯 TIME ESTIMATES

- Base Processor: 5 min
- Default Processor: 15 min
- Recipe Processor: 20 min
- Comedy Processor: 20 min
- Education Processor: 25 min
- Movie List Processor: 45 min (includes API testing)
- Song List Processor: 45 min (includes API testing)
- Router: 10 min
- Integration: 15 min

**Total: ~3-4 hours** (with testing)

---

## 🎉 SUCCESS CRITERIA

Phase 3 is complete when:

1. ✅ You can analyze a recipe video and get ingredients
2. ✅ You can analyze a movie list and get TMDB data
3. ✅ You can analyze a song list and get Spotify data
4. ✅ All processors return valid structured output
5. ✅ Error handling works (no crashes)
6. ✅ Router correctly maps categories
7. ✅ Integrated into analyze endpoint

**Then you're ready for Phase 4: Frontend!** 🚀