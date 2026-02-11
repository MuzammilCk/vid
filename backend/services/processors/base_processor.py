"""
Base processor for category-specific video analysis.

This module provides the abstract base class that all category processors
must inherit from. It defines the common interface and helper methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from models.schemas import ExtractionResult


class BaseProcessor(ABC):
    """
    Abstract base class for all category-specific processors.
    
    Each video category (movie_list, song_list, recipe, etc.) should have
    its own processor that inherits from this class and implements the
    process() method to return structured, category-specific data.
    """
    
    @abstractmethod
    async def process(self, extraction: ExtractionResult) -> Dict[str, Any]:
        """
        Process the extraction result and return structured output.
        
        This method must be implemented by all subclasses. It should analyze
        the video data and return a dictionary with category-specific structured
        information.
        
        Args:
            extraction: Complete video extraction result from Phase 1
            
        Returns:
            Dict[str, Any]: Structured output specific to the video category.
                Must include at minimum: {"type": "category_name", ...}
                
        Raises:
            NotImplementedError: If subclass doesn't implement this method
            
        Example:
            >>> processor = RecipeProcessor()
            >>> result = await processor.process(extraction)
            >>> print(result["type"])
            'recipe'
        """
        pass
    
    def get_text_content(self, extraction: ExtractionResult) -> str:
        """
        Get the best available text content from the video extraction.
        
        Returns text content in priority order:
        1. Captions (if available) - most accurate
        2. Transcript (if available) - from Whisper transcription
        3. Description (if available) - video metadata
        4. Empty string (if nothing available)
        
        Args:
            extraction: Video extraction result
            
        Returns:
            str: Best available text content, or empty string if none available
            
        Example:
            >>> text = self.get_text_content(extraction)
            >>> if text:
            ...     # Process the text
            ...     pass
        """
        return (
            extraction.captions
            or extraction.transcript
            or extraction.metadata.description
            or ""
        )
