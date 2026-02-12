"""
Test script for FULL MovieListProcessor with a REAL YouTube video.

This script:
1. Downloads video data (transcript + frames) using extract_all
2. Runs the full MovieListProcessor (Extraction + TMDB Enrichment)
3. Prints the final enriched results
"""

import asyncio
from services.youtube_extractor import extract_all
from services.processors.movie_list import MovieListProcessor


async def test():
    print("\n" + "="*60)
    print("🎥 MOVIE LIST PROCESSOR - REAL VIDEO TEST")
    print("="*60 + "\n")
    
    # URL input
    url = input("Enter a 'Top Movies' video URL: ")
    
    print("\n⏳ Step 1: Extracting video data (Transcript + Frames)...")
    try:
        extraction = await extract_all(url)
        print(f"✅ Video found: {extraction.metadata.title}")
        print(f"   Transcript length: {len(extraction.transcript) if extraction.transcript else 0} chars")
        print(f"   Key frames extracted: {len(extraction.key_frame_paths)}")
            
        print("\n⏳ Step 2: Running MovieListProcessor (Extraction + TMDB Enrichment)...")
        processor = MovieListProcessor()
        result = await processor.process(extraction)
        
        print("\n" + "="*60)
        print("✅ FINAL RESULTS")
        print("="*60)
        
        print(f"Extraction Method: {result.get('extraction_method')}")
        print(f"Movies Found: {result.get('count')}\n")
        
        for m in result.get('movies', []):
            print(f"🎬 #{m.get('rank')} {m.get('title')} ({m.get('year')})")
            
            # TMDB Details
            if m.get('tmdb_id'):
                print(f"   ⭐ TMDB Rating: {m.get('tmdb_rating')} | ID: {m.get('tmdb_id')}")
                print(f"   🎭 Genres: {', '.join(m.get('genres', []))}")
                print(f"   🎬 Director: {m.get('director')}")
                print(f"   📝 Overview: {m.get('overview', '')[:100]}...")
                
                streaming = m.get('streaming', {})
                if streaming.get('flatrate'):
                    print(f"   📺 Stream: {', '.join(streaming['flatrate'])}")
                if streaming.get('rent'):
                    print(f"   💰 Rent: {', '.join(streaming['rent'][:3])}")
            else:
                print("   ⚠️ No TMDB data found")
            print("-" * 40)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
