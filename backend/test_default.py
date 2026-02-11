"""
Test script for DefaultProcessor.

Tests the general-purpose video analyzer with a real YouTube video.
"""

import asyncio
from services.youtube_extractor import extract_all
from services.processors.default import DefaultProcessor


async def test():
    """Test DefaultProcessor with a YouTube video."""
    print("\n" + "="*60)
    print("DEFAULT PROCESSOR TEST")
    print("="*60 + "\n")
    
    url = input("Enter YouTube URL to test: ")
    
    print("\n⏳ Extracting video data...")
    extraction = await extract_all(url)
    
    print(f"\n✅ Extracted: {extraction.metadata.title}")
    print(f"   Channel: {extraction.metadata.channel_name}")
    print(f"   Duration: {extraction.metadata.duration_seconds}s")
    
    print("\n⏳ Processing with DefaultProcessor...")
    processor = DefaultProcessor()
    result = await processor.process(extraction)
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"\n✅ Type: {result['type']}")
    print(f"\n✅ Summary:\n   {result['summary']}")
    print(f"\n✅ Key Points ({len(result['key_points'])}):")
    for i, point in enumerate(result['key_points'], 1):
        print(f"   {i}. {point}")
    print(f"\n✅ Topics: {', '.join(result['topics'])}")
    print(f"\n✅ Sentiment: {result['sentiment']}")
    print(f"\n✅ Transcript length: {len(result['transcript'])} characters")
    
    # Assertions
    assert result['type'] == 'general', "Type must be 'general'"
    assert 'summary' in result, "Must have summary"
    assert isinstance(result['key_points'], list), "key_points must be a list"
    assert result['sentiment'] in ['positive', 'negative', 'neutral'], "Invalid sentiment"
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test())
