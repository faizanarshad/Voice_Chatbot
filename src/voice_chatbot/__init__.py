"""
AI Voice Assistant Pro - Main Application Package

This package contains the core functionality for the AI Voice Assistant Pro,
including voice recognition, text-to-speech, NLP processing, and LLM integration.
"""

from .core.app import VoiceChatbot
from .core.config import Config

__all__ = ['VoiceChatbot', 'Config']
