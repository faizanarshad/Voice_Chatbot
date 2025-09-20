import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Voice Chatbot"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5001))
    
    # Speech Recognition settings
    SPEECH_RECOGNITION_TIMEOUT = int(os.getenv('SPEECH_RECOGNITION_TIMEOUT', 5))
    SPEECH_RECOGNITION_PHRASE_TIME_LIMIT = int(os.getenv('SPEECH_RECOGNITION_PHRASE_TIME_LIMIT', 10))
    SPEECH_RECOGNITION_AMBIENT_NOISE_DURATION = int(os.getenv('SPEECH_RECOGNITION_AMBIENT_NOISE_DURATION', 1))
    
    # Text-to-Speech settings
    TTS_RATE = int(os.getenv('TTS_RATE', 150))  # Medium speed for better flow
    TTS_VOLUME = float(os.getenv('TTS_VOLUME', 1.0))  # Full volume
    TTS_VOICE_ID = os.getenv('TTS_VOICE_ID', None)  # Will use default if not set
    
    # NLP settings
    NLP_CONFIDENCE_THRESHOLD = float(os.getenv('NLP_CONFIDENCE_THRESHOLD', 0.7))
    NLP_MAX_CONVERSATION_HISTORY = int(os.getenv('NLP_MAX_CONVERSATION_HISTORY', 50))
    
    # LLM Integration Settings
    USE_LLM = os.getenv('USE_LLM', 'false').lower() == 'true'
    ACTIVE_LLM = os.getenv('ACTIVE_LLM', 'openai')
    
    # API Keys (optional - for enhanced features)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', None)
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', None)
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', None)
    
    # Ollama Configuration (Local LLM)
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'voice_chatbot.log')
    
    # Security settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # Feature flags
    ENABLE_VOICE_RECOGNITION = os.getenv('ENABLE_VOICE_RECOGNITION', 'True').lower() == 'true'
    ENABLE_TEXT_TO_SPEECH = os.getenv('ENABLE_TEXT_TO_SPEECH', 'True').lower() == 'true'
    ENABLE_ADVANCED_NLP = os.getenv('ENABLE_ADVANCED_NLP', 'True').lower() == 'true'
    ENABLE_LLM_INTEGRATION = os.getenv('ENABLE_LLM_INTEGRATION', 'True').lower() == 'true'
    ENABLE_WEATHER_API = os.getenv('ENABLE_WEATHER_API', 'False').lower() == 'true'
    ENABLE_NEWS_API = os.getenv('ENABLE_NEWS_API', 'False').lower() == 'true'
    
    # Database settings (for future use)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///voice_chatbot.db')
    
    # Cache settings
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    @classmethod
    def get_speech_config(cls):
        """Get speech recognition configuration"""
        return {
            'timeout': cls.SPEECH_RECOGNITION_TIMEOUT,
            'phrase_time_limit': cls.SPEECH_RECOGNITION_PHRASE_TIME_LIMIT,
            'ambient_noise_duration': cls.SPEECH_RECOGNITION_AMBIENT_NOISE_DURATION
        }
    
    @classmethod
    def get_tts_config(cls):
        """Get text-to-speech configuration"""
        return {
            'rate': cls.TTS_RATE,
            'volume': cls.TTS_VOLUME,
            'voice_id': cls.TTS_VOICE_ID
        }
    
    @classmethod
    def get_nlp_config(cls):
        """Get NLP configuration"""
        return {
            'confidence_threshold': cls.NLP_CONFIDENCE_THRESHOLD,
            'max_conversation_history': cls.NLP_MAX_CONVERSATION_HISTORY
        }
    
    @classmethod
    def get_llm_config(cls):
        """Get LLM configuration"""
        return {
            'use_llm': cls.USE_LLM,
            'active_llm': cls.ACTIVE_LLM,
            'openai_api_key': cls.OPENAI_API_KEY,
            'anthropic_api_key': cls.ANTHROPIC_API_KEY,
            'ollama_base_url': cls.OLLAMA_BASE_URL,
            'ollama_model': cls.OLLAMA_MODEL
        }
    
    @classmethod
    def validate_config(cls):
        """Validate configuration and return any issues"""
        issues = []
        
        # Check required settings
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'your-secret-key-here':
            issues.append("Warning: SECRET_KEY should be set for production")
        
        # Check LLM configuration
        if cls.USE_LLM:
            if cls.ACTIVE_LLM == 'openai' and not cls.OPENAI_API_KEY:
                issues.append("Warning: OPENAI_API_KEY required for OpenAI LLM integration")
            elif cls.ACTIVE_LLM == 'anthropic' and not cls.ANTHROPIC_API_KEY:
                issues.append("Warning: ANTHROPIC_API_KEY required for Anthropic LLM integration")
            elif cls.ACTIVE_LLM == 'ollama':
                issues.append("Info: Using local Ollama LLM - ensure Ollama is running")
        
        # Check API keys if features are enabled
        if cls.ENABLE_WEATHER_API and not cls.WEATHER_API_KEY:
            issues.append("Warning: WEATHER_API_KEY required for weather features")
        
        if cls.ENABLE_NEWS_API and not cls.NEWS_API_KEY:
            issues.append("Warning: NEWS_API_KEY required for news features")
        
        return issues
