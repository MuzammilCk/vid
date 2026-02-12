"""
Test script for the complete MovieListProcessor class.

Tests:
1. Multimodal extraction capability (simulated)
2. TMDB enrichment integration
3. Final output structure
"""

import asyncio
from services.processors.movie_list import MovieListProcessor
from models.schemas import ExtractionResult, VideoMetadata


async def test_full_processor():
    print("\n" + "="*60)
    print("🎥 MOVIE LIST PROCESSOR - FULL INTEGRATION TEST")
    print("="*60 + "\n")
    
    # 1. Simulate Extraction Result
    print("📝 Creating mock extraction data...")
    mock_meta = VideoMetadata(
        video_id="test_vid_123",
        title="Top 5 Action Movies of 2023",
        description="Here are the best action movies released this year.",
        channel_name="MovieTest",
        channel_id="UC123",
        duration_seconds=600,
        thumbnail_url="http://example.com/thumb.jpg",
        published_at="2024-01-01T00:00:00Z",
        category_id="1"
    )
    
    # Simulate a transcript that might come from a video
    mock_transcript = """
    Welcome to our top 10 movies countdown!
    
    Number 10: Dune Part Two. Denis Villeneuve's epic continues with an amazing 
    cast. Released in 2024, this sci-fi masterpiece takes us deeper into Arrakis.
    
    Number 9: Oppenheimer from 2023. Christopher Nolan's biographical thriller
    about the father of the atomic bomb won multiple Oscars.
    
    Number 8: Everything Everywhere All at Once. The 2022 multiverse film
    that swept the awards season with its creative storytelling.
    """
    
    mock_extraction = ExtractionResult(
        metadata=mock_meta,
        captions=mock_transcript,
        transcript=mock_transcript,
        key_frame_paths=[], # Emtpy for this synthetic test, but class supports them
        top_comments=[]
    )
    
    # 2. Initialize Processor
    print("⚙️ Initializing MovieListProcessor...")
    processor = MovieListProcessor()
    
    # 3. Process
    print("⏳ Processing (Extraction + Enrichment)...")
    result = await processor.process(mock_extraction)
    
    # 4. Verify Results
    print("\n" + "="*60)
    print("✅ FINAL RESULTS")
    print("="*60)
    
    print(f"Type: {result['type']}")
    print(f"Count: {result['count']}")
    print(f"Method: {result['extraction_method']}")
    print("\nMovies Found:")
    
    for m in result['movies']:
        print(f"\n🎬 #{m.get('rank')} {m.get('title')} ({m.get('year')})")
        print(f"   TMDB Rating: {m.get('tmdb_rating', 'N/A')}")
        print(f"   Overview: {m.get('overview', '')[:100]}...")
        if m.get('streaming', {}).get('flatrate'):
            print(f"   Streaming: {', '.join(m['streaming']['flatrate'])}")
            
    # Assertions
    print(f"Found {len(result['movies'])} movies")
    assert result['type'] == 'movie_list'
    assert len(result['movies']) >= 2 # Allow 2/3 to pass
    assert result['movies'][0].get('tmdb_id') is not None
    print("\n✅ Processor integration test passed!")


if __name__ == "__main__":
    asyncio.run(test_full_processor())
