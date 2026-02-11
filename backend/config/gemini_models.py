"""
Gemini API Model Configuration

This file contains all available Gemini models as of February 2026.
Only use models listed here to avoid 404 errors.

Reference: https://ai.google.dev/gemini-api/docs/models/gemini
"""

from enum import Enum
from typing import Dict, Any


class GeminiModel(str, Enum):
    """Available Gemini models with their official model codes."""
    
    # ========================================================================
    # GEMINI 3 SERIES (Latest - Most Intelligent)
    # ========================================================================
    
    # Gemini 3 Pro - Most intelligent multimodal model
    GEMINI_3_PRO_PREVIEW = "gemini-3-pro-preview"
    GEMINI_3_PRO_IMAGE_PREVIEW = "gemini-3-pro-image-preview"
    
    # Gemini 3 Flash - Balanced for speed and intelligence
    GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
    
    # ========================================================================
    # GEMINI 2.5 SERIES (Recommended for Production)
    # ========================================================================
    
    # Gemini 2.5 Flash - Best price-performance (RECOMMENDED)
    GEMINI_2_5_FLASH = "gemini-2.5-flash"  # Stable
    GEMINI_2_5_FLASH_PREVIEW = "gemini-2.5-flash-preview-09-2025"
    GEMINI_2_5_FLASH_IMAGE = "gemini-2.5-flash-image"
    GEMINI_2_5_FLASH_LIVE = "gemini-2.5-flash-native-audio-preview-12-2025"
    GEMINI_2_5_FLASH_TTS = "gemini-2.5-flash-preview-tts"
    
    # Gemini 2.5 Flash-Lite - Ultra fast and cost-efficient
    GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite"  # Stable
    GEMINI_2_5_FLASH_LITE_PREVIEW = "gemini-2.5-flash-lite-preview-09-2025"
    
    # Gemini 2.5 Pro - Advanced thinking model
    GEMINI_2_5_PRO = "gemini-2.5-pro"  # Stable
    GEMINI_2_5_PRO_TTS = "gemini-2.5-pro-preview-tts"
    
    # ========================================================================
    # GEMINI 2.0 SERIES (Deprecated - Shutdown March 31, 2026)
    # ========================================================================
    
    # Gemini 2.0 Flash - DEPRECATED
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_FLASH_001 = "gemini-2.0-flash-001"
    GEMINI_2_0_FLASH_EXP = "gemini-2.0-flash-exp"  # Experimental
    
    # Gemini 2.0 Flash-Lite - DEPRECATED
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
    GEMINI_2_0_FLASH_LITE_001 = "gemini-2.0-flash-lite-001"


# ============================================================================
# Model Capabilities and Metadata
# ============================================================================

MODEL_METADATA: Dict[GeminiModel, Dict[str, Any]] = {
    # Gemini 3 Series
    GeminiModel.GEMINI_3_PRO_PREVIEW: {
        "name": "Gemini 3 Pro Preview",
        "input_types": ["text", "image", "video", "audio", "pdf"],
        "output_types": ["text"],
        "input_token_limit": 1_048_576,
        "output_token_limit": 65_536,
        "supports_function_calling": True,
        "supports_structured_output": True,
        "supports_thinking": True,
        "knowledge_cutoff": "January 2025",
        "status": "preview",
        "recommended_for": "Most intelligent multimodal tasks"
    },
    
    GeminiModel.GEMINI_3_FLASH_PREVIEW: {
        "name": "Gemini 3 Flash Preview",
        "input_types": ["text", "image", "video", "audio", "pdf"],
        "output_types": ["text"],
        "input_token_limit": 1_048_576,
        "output_token_limit": 65_536,
        "supports_function_calling": True,
        "supports_structured_output": True,
        "supports_thinking": True,
        "knowledge_cutoff": "January 2025",
        "status": "preview",
        "recommended_for": "Balanced speed and intelligence"
    },
    
    # Gemini 2.5 Series (RECOMMENDED)
    GeminiModel.GEMINI_2_5_FLASH: {
        "name": "Gemini 2.5 Flash",
        "input_types": ["text", "image", "video", "audio"],
        "output_types": ["text"],
        "input_token_limit": 1_048_576,
        "output_token_limit": 65_536,
        "supports_function_calling": True,
        "supports_structured_output": True,
        "supports_thinking": True,
        "knowledge_cutoff": "January 2025",
        "status": "stable",
        "recommended_for": "Production - best price-performance"
    },
    
    GeminiModel.GEMINI_2_5_FLASH_LITE: {
        "name": "Gemini 2.5 Flash-Lite",
        "input_types": ["text", "image", "video", "audio", "pdf"],
        "output_types": ["text"],
        "input_token_limit": 1_048_576,
        "output_token_limit": 65_536,
        "supports_function_calling": True,
        "supports_structured_output": True,
        "supports_thinking": True,
        "knowledge_cutoff": "January 2025",
        "status": "stable",
        "recommended_for": "High throughput, cost efficiency"
    },
    
    GeminiModel.GEMINI_2_5_PRO: {
        "name": "Gemini 2.5 Pro",
        "input_types": ["text", "image", "video", "audio", "pdf"],
        "output_types": ["text"],
        "input_token_limit": 1_048_576,
        "output_token_limit": 65_536,
        "supports_function_calling": True,
        "supports_structured_output": True,
        "supports_thinking": True,
        "knowledge_cutoff": "January 2025",
        "status": "stable",
        "recommended_for": "Complex reasoning, large datasets"
    },
    
    # Gemini 2.0 Series (DEPRECATED)
    GeminiModel.GEMINI_2_0_FLASH: {
        "name": "Gemini 2.0 Flash",
        "input_types": ["text", "image", "video", "audio"],
        "output_types": ["text"],
        "input_token_limit": 1_048_576,
        "output_token_limit": 8_192,
        "supports_function_calling": True,
        "supports_structured_output": True,
        "supports_thinking": False,
        "knowledge_cutoff": "August 2024",
        "status": "deprecated",
        "deprecation_date": "March 31, 2026",
        "recommended_for": "DEPRECATED - Use Gemini 2.5 Flash instead"
    },
}


# ============================================================================
# Recommended Models for VidBrain AI
# ============================================================================

class RecommendedModels:
    """Recommended models for different use cases in VidBrain AI."""
    
    # Primary model for classification (fast, multimodal)
    CLASSIFICATION = GeminiModel.GEMINI_2_5_FLASH
    
    # Fallback model for classification (more stable)
    CLASSIFICATION_FALLBACK = GeminiModel.GEMINI_2_5_PRO
    
    # Default processor (general analysis)
    DEFAULT_PROCESSOR = GeminiModel.GEMINI_2_5_FLASH
    
    # Recipe processor (structured extraction)
    RECIPE_PROCESSOR = GeminiModel.GEMINI_2_5_FLASH_LITE
    
    # Comedy processor (creative analysis)
    COMEDY_PROCESSOR = GeminiModel.GEMINI_2_5_FLASH
    
    # Education processor (factual content)
    EDUCATION_PROCESSOR = GeminiModel.GEMINI_2_5_PRO
    
    # Movie/Song list processors (batch processing)
    LIST_PROCESSOR = GeminiModel.GEMINI_2_5_FLASH_LITE


# ============================================================================
# Helper Functions
# ============================================================================

def get_model_info(model: GeminiModel) -> Dict[str, Any]:
    """
    Get metadata for a specific model.
    
    Args:
        model: GeminiModel enum value
        
    Returns:
        dict: Model metadata
    """
    return MODEL_METADATA.get(model, {})


def is_model_deprecated(model: GeminiModel) -> bool:
    """
    Check if a model is deprecated.
    
    Args:
        model: GeminiModel enum value
        
    Returns:
        bool: True if deprecated
    """
    info = get_model_info(model)
    return info.get("status") == "deprecated"


def get_stable_models() -> list[GeminiModel]:
    """
    Get all stable (production-ready) models.
    
    Returns:
        list: List of stable GeminiModel values
    """
    return [
        model for model, info in MODEL_METADATA.items()
        if info.get("status") == "stable"
    ]


def get_recommended_model_for_task(task: str) -> GeminiModel:
    """
    Get recommended model for a specific task.
    
    Args:
        task: Task name (classification, default, recipe, etc.)
        
    Returns:
        GeminiModel: Recommended model
    """
    task_map = {
        "classification": RecommendedModels.CLASSIFICATION,
        "default": RecommendedModels.DEFAULT_PROCESSOR,
        "recipe": RecommendedModels.RECIPE_PROCESSOR,
        "comedy": RecommendedModels.COMEDY_PROCESSOR,
        "education": RecommendedModels.EDUCATION_PROCESSOR,
        "list": RecommendedModels.LIST_PROCESSOR,
    }
    
    return task_map.get(task.lower(), RecommendedModels.DEFAULT_PROCESSOR)
