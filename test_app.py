#!/usr/bin/env python3
"""
Simple test script for AI Voice Assistant Pro
Tests basic functionality and LLM integration
"""

import requests
import json
import time

def test_basic_functionality():
    """Test basic application functionality"""
    print("🧪 Testing AI Voice Assistant Pro")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # Test 1: Check if app is running
    print("\n1. Testing application status...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Application is running")
            print(f"   📊 LLM Enabled: {data.get('llm_enabled', False)}")
            print(f"   🤖 Active LLM: {data.get('active_llm', 'none')}")
            print(f"   🔧 System Ready: {data.get('system_ready', False)}")
        else:
            print(f"   ❌ Application returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Cannot connect to application: {e}")
        print("   💡 Make sure to run 'python app.py' first")
        return False
    
    # Test 2: Test text processing
    print("\n2. Testing text processing...")
    test_messages = [
        "Hello, how are you?",
        "What time is it?",
        "Tell me a joke",
        "What can you do?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        try:
            response = requests.post(
                f"{base_url}/api/process-text",
                json={"text": message},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Test {i}: '{message}'")
                print(f"      Response: {data.get('response', 'No response')[:100]}...")
            else:
                print(f"   ❌ Test {i} failed with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Test {i} failed: {e}")
    
    # Test 3: Test LLM integration (if enabled)
    print("\n3. Testing LLM integration...")
    try:
        response = requests.post(
            f"{base_url}/api/process-text",
            json={"text": "Explain artificial intelligence in simple terms"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            # Check if it's a fallback response
            if any(fallback in response_text for fallback in [
                "I understand you said:", "Thanks for your message:", 
                "I received:", "Your message:"
            ]):
                print("   ⚠️  LLM integration not active (using fallback responses)")
                print("   💡 Add OpenAI API key to .env file to enable LLM features")
            else:
                print("   ✅ LLM integration is working!")
                print(f"      Sample response: {response_text[:150]}...")
        else:
            print(f"   ❌ LLM test failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ LLM test failed: {e}")
    
    # Test 4: Test features endpoint
    print("\n4. Testing features endpoint...")
    try:
        response = requests.get(f"{base_url}/api/features", timeout=5)
        if response.status_code == 200:
            data = response.json()
            features = data.get('new_features', {})
            print(f"   ✅ Available features: {len(features)}")
            for feature_name, description in features.items():
                print(f"      • {feature_name.replace('_', ' ').title()}")
        else:
            print(f"   ❌ Features test failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Features test failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
    print("\n💡 Next steps:")
    print("   1. Open http://localhost:5001 in your browser")
    print("   2. Try voice commands or text input")
    print("   3. Add OpenAI API key to .env for enhanced AI features")

if __name__ == "__main__":
    test_basic_functionality()
