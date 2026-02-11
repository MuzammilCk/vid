"""
Configuration package for VidBrain AI.
"""

from .gemini_models import (
    GeminiModel,
    RecommendedModels,
    get_model_info,
    is_model_deprecated,
    get_stable_models,
    get_recommended_model_for_task
)

__all__ = [
    'GeminiModel',
    'RecommendedModels',
    'get_model_info',
    'is_model_deprecated',
    'get_stable_models',
    'get_recommended_model_for_task'
]
