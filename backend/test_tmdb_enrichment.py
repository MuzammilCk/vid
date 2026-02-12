"""
Test script for TMDB enrichment function.

Tests the enrich_movie_with_tmdb function with sample movie titles.
"""

import asyncio
from services.processors.movie_list import enrich_movie_with_tmdb


async def test():
    """Test TMDB enrichment with known movies."""
    print("\n" + "="*60)
    print("TMDB ENRICHMENT TEST")
    print("="*60 + "\n")
    
    # Test movies
    test_movies = [
        {"title": "Dune Part Two", "year": 2024},
        {"title": "Oppenheimer", "year": 2023},
        {"title": "The Matrix", "year": 1999},
    ]
    
    for movie in test_movies:
        print(f"\n⏳ Enriching: {movie['title']} ({movie['year']})")
        
        result = await enrich_movie_with_tmdb(movie['title'], movie['year'])
        
        if result:
            print(f"✅ Found: {result['title']}")
            print(f"   TMDB ID: {result['tmdb_id']}")
            print(f"   Rating: {result['tmdb_rating']}/10")
            print(f"   Genres: {', '.join(result['genres'])}")
            print(f"   Director: {result['director']}")
            print(f"   Runtime: {result['runtime']} min")
            print(f"   Poster: {result['poster_url'][:50] if result['poster_url'] else 'None'}...")
            
            streaming = result['streaming']
            if streaming['flatrate']:
                print(f"   Streaming on: {', '.join(streaming['flatrate'])}")
            if streaming['rent']:
                print(f"   Rent on: {', '.join(streaming['rent'][:3])}")
        else:
            print(f"❌ Not found or error")
    
    print("\n" + "="*60)
    print("✅ TMDB ENRICHMENT TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test())
