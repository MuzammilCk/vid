"""
Test script for movie extraction function.

Tests the extract_movies_from_transcript function with sample data.
"""

import asyncio
from services.processors.movie_list import extract_movies_from_transcript


async def test():
    """Test movie extraction with sample transcript."""
    print("\n" + "="*60)
    print("MOVIE EXTRACTION TEST")
    print("="*60 + "\n")
    
    # Sample transcript from a movie list video
    transcript = """
    Welcome to our top 10 sci-fi movies countdown!
    
    Number 10: Dune Part Two. Denis Villeneuve's epic continues with an amazing 
    cast. Released in 2024, this sci-fi masterpiece takes us deeper into Arrakis.
    
    Number 9: Oppenheimer from 2023. Christopher Nolan's biographical thriller
    about the father of the atomic bomb won multiple Oscars.
    
    Number 8: Everything Everywhere All at Once. The 2022 multiverse film
    that swept the awards season with its creative storytelling.
    
    Number 7: Interstellar. Nolan's 2014 space epic about love and time.
    
    Number 6: Blade Runner 2049. The 2017 sequel that lived up to the original.
    
    Number 5: Arrival from 2016. Amy Adams in a thoughtful alien contact story.
    
    Number 4: The Matrix from 1999. The film that changed sci-fi forever.
    
    Number 3: Inception. Another Nolan masterpiece from 2010.
    
    Number 2: The Prestige. Released in 2006, this is Nolan's magician thriller.
    
    Number 1: The Dark Knight. The 2008 superhero film that transcended the genre.
    """
    
    title = "Top 10 Sci-Fi Movies of the Decade"
    
    print("⏳ Extracting movies from transcript...")
    movies = await extract_movies_from_transcript(transcript, title)
    
    print("\n" + "="*60)
    print("EXTRACTION RESULTS")
    print("="*60)
    print(f"\n✅ Extracted {len(movies)} movies:\n")
    
    for movie in movies:
        year_str = f"({movie.get('year', 'unknown')})" if movie.get('year') else "(year unknown)"
        print(f"  {movie['rank']}. {movie['title']} {year_str}")
    
    # Assertions
    assert len(movies) > 0, "Should extract at least one movie"
    assert 'title' in movies[0], "Movies should have 'title' field"
    assert 'rank' in movies[0], "Movies should have 'rank' field"
    assert 'year' in movies[0], "Movies should have 'year' field"
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")
    
    # Show first movie details
    print(f"First movie details: {movies[0]}")


if __name__ == "__main__":
    asyncio.run(test())
