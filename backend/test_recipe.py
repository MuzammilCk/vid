"""
Test script for RecipeProcessor.

Tests recipe extraction with a real cooking video.
"""

import asyncio
from services.youtube_extractor import extract_all
from services.processors.recipe import RecipeProcessor


async def test():
    """Test RecipeProcessor with a cooking video."""
    print("\n" + "="*60)
    print("RECIPE PROCESSOR TEST")
    print("="*60 + "\n")
    
    url = input("Enter a recipe video URL: ")
    
    print("\n⏳ Extracting video data...")
    extraction = await extract_all(url)
    
    print(f"\n✅ Extracted: {extraction.metadata.title}")
    print(f"   Channel: {extraction.metadata.channel_name}")
    print(f"   Duration: {extraction.metadata.duration_seconds}s")
    
    print("\n⏳ Processing with RecipeProcessor...")
    processor = RecipeProcessor()
    result = await processor.process(extraction)
    
    print("\n" + "="*60)
    print("RECIPE RESULTS")
    print("="*60)
    print(f"\n✅ Dish: {result['dish_name']}")
    print(f"✅ Cuisine: {result['cuisine']}")
    print(f"✅ Difficulty: {result['difficulty']}")
    print(f"✅ Prep Time: {result['prep_time']}")
    print(f"✅ Cook Time: {result['cook_time']}")
    print(f"✅ Servings: {result['servings']}")
    print(f"✅ Transcript: {result.get('transcript_completeness', 'unknown')}")
    
    print(f"\n✅ Ingredients ({len(result['ingredients'])}):")
    for i, ing in enumerate(result['ingredients'][:5], 1):
        print(f"   {i}. {ing.get('quantity', '')} {ing.get('item', '')}")
        if ing.get('notes'):
            print(f"      Note: {ing['notes']}")
    if len(result['ingredients']) > 5:
        print(f"   ... and {len(result['ingredients']) - 5} more")
    
    print(f"\n✅ Steps ({len(result['steps'])}):")
    for step in result['steps'][:3]:
        timestamp = f" [{step.get('timestamp')}]" if step.get('timestamp') else ""
        print(f"   {step.get('step', '?')}. {step.get('instruction', '')[:80]}...{timestamp}")
    if len(result['steps']) > 3:
        print(f"   ... and {len(result['steps']) - 3} more steps")
    
    if result.get('tips'):
        print(f"\n✅ Tips ({len(result['tips'])}):")
        for tip in result['tips'][:2]:
            print(f"   • {tip}")
    
    print(f"\n✅ Nutrition (per serving):")
    nutrition = result.get('nutrition_estimate', {})
    print(f"   Calories: {nutrition.get('calories', 'N/A')}")
    print(f"   Protein: {nutrition.get('protein', 'N/A')}")
    print(f"   Carbs: {nutrition.get('carbs', 'N/A')}")
    print(f"   Fat: {nutrition.get('fat', 'N/A')}")
    
    # Assertions
    assert result['type'] == 'recipe', "Type must be 'recipe'"
    assert 'dish_name' in result, "Must have dish_name"
    assert isinstance(result['ingredients'], list), "ingredients must be a list"
    assert isinstance(result['steps'], list), "steps must be a list"
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")
    
    # Show first ingredient and step details
    if result['ingredients']:
        print(f"First ingredient details: {result['ingredients'][0]}")
    if result['steps']:
        print(f"First step details: {result['steps'][0]}")


if __name__ == "__main__":
    asyncio.run(test())
