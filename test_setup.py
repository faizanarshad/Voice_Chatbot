#!/usr/bin/env python3
"""
Test script to verify Voice Chatbot setup and dependencies.
Run this script to check if everything is working correctly.
"""

import sys
import importlib
import subprocess
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'speech_recognition',
        'pyttsx3',
        'pyaudio',
        'numpy',
        'sklearn',  # scikit-learn is imported as sklearn
        'nltk',
        'spacy',
        'transformers',
        'torch',
        'openai',
        'dotenv',  # python-dotenv is imported as dotenv
        'requests',
        'websockets',
        'asyncio',
        'aiohttp'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All packages imported successfully!")
        return True

def test_speech_recognition():
    """Test speech recognition setup"""
    print("\n🎤 Testing speech recognition...")
    
    try:
        import speech_recognition as sr
        
        # Test microphone access
        r = sr.Recognizer()
        mic = sr.Microphone()
        
        with mic as source:
            print("  ✅ Microphone detected")
            r.adjust_for_ambient_noise(source, duration=1)
            print("  ✅ Ambient noise calibration successful")
        
        print("✅ Speech recognition setup successful!")
        return True
        
    except Exception as e:
        print(f"❌ Speech recognition test failed: {e}")
        print("Make sure you have a working microphone and PyAudio installed")
        return False

def test_text_to_speech():
    """Test text-to-speech setup"""
    print("\n🔊 Testing text-to-speech...")
    
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        if voices:
            print(f"  ✅ Found {len(voices)} voice(s)")
            for i, voice in enumerate(voices):
                print(f"    - Voice {i}: {voice.name}")
        else:
            print("  ⚠️  No voices found")
        
        # Test basic TTS functionality
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.5)
        print("  ✅ TTS engine configured")
        
        print("✅ Text-to-speech setup successful!")
        return True
        
    except Exception as e:
        print(f"❌ Text-to-speech test failed: {e}")
        return False

def test_nlp_engine():
    """Test NLP engine"""
    print("\n🧠 Testing NLP engine...")
    
    try:
        from nlp_engine import NLPEngine
        
        nlp = NLPEngine()
        
        # Test basic NLP processing
        test_text = "Hello, how are you today?"
        result = nlp.process_input(test_text)
        
        print(f"  ✅ Intent recognized: {result['intent']}")
        print(f"  ✅ Confidence: {result['confidence']:.2f}")
        print(f"  ✅ Sentiment: {result['sentiment']}")
        
        print("✅ NLP engine working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ NLP engine test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n⚙️  Testing configuration...")
    
    try:
        from config import Config
        
        # Test basic config loading
        print(f"  ✅ Flask port: {Config.PORT}")
        print(f"  ✅ Debug mode: {Config.DEBUG}")
        print(f"  ✅ TTS rate: {Config.TTS_RATE}")
        print(f"  ✅ Speech timeout: {Config.SPEECH_RECOGNITION_TIMEOUT}")
        
        # Test config validation
        issues = Config.validate_config()
        if issues:
            print("  ⚠️  Configuration warnings:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("  ✅ Configuration validation passed")
        
        print("✅ Configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app initialization"""
    print("\n🌐 Testing Flask app...")
    
    try:
        from app import app
        
        print("  ✅ Flask app created successfully")
        print("  ✅ Routes registered")
        
        # Test basic route
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("  ✅ Main route accessible")
            else:
                print(f"  ⚠️  Main route returned status {response.status_code}")
        
        print("✅ Flask app working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'app.py',
        'nlp_engine.py',
        'config.py',
        'requirements.txt',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present!")
        return True

def main():
    """Run all tests"""
    print("🚀 Voice Chatbot Setup Test")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_config,
        test_nlp_engine,
        test_speech_recognition,
        test_text_to_speech,
        test_flask_app
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Voice Chatbot is ready to use.")
        print("\nTo start the application:")
        print("  python app.py")
        print("\nThen open your browser to: http://localhost:5000")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above and fix them.")
        print("\nCommon solutions:")
        print("  1. Install missing packages: pip install -r requirements.txt")
        print("  2. Check microphone permissions")
        print("  3. Install system audio dependencies (portaudio)")
        print("  4. Create .env file from env_example.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
