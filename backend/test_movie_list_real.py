"""
Test script for movie extraction with a REAL YouTube video.

This script:
1. Downloads video metadata/transcript using extract_all
2. Runs the movie extraction function on the real transcript
3. Prints the results
"""

import asyncio
from services.youtube_extractor import extract_all
from services.processors.movie_list import extract_movies_from_transcript


async def test():
    print("\n" + "="*60)
    print("MOVIE EXTRACTION TEST - REAL VIDEO")
    print("="*60 + "\n")
    
    # URL input
    url = input("Enter a 'Top Movies' video URL: ")
    
    print("\n⏳ Step 1: Extracting video data (this may take a few seconds)...")
    try:
        extraction = await extract_all(url)
        print(f"✅ Video found: {extraction.metadata.title}")
        
        # Get transcript
        transcript = extraction.captions or extraction.transcript
        if not transcript:
            print("❌ No transcript/captions found for this video!")
            # Fallback to description
            print("⚠️ Trying description instead...")
            transcript = extraction.metadata.description
            
        print(f"✅ Text content length: {len(transcript)} chars")
            
        print("\n⏳ Step 2: Extracting movies with Gemini...")
        movies = await extract_movies_from_transcript(transcript, extraction.metadata.title)
        
        print("\n" + "="*60)
        print("EXTRACTION RESULTS")
        print("="*60)
        print(f"\nFound {len(movies)} movies:\n")
        
        for movie in movies:
            year_str = f"({movie.get('year', 'unknown')})" if movie.get('year') else ""
            print(f"  {movie['rank']}. {movie['title']} {year_str}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
