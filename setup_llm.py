#!/usr/bin/env python3
"""
LLM Setup Script for Voice Chatbot
This script helps you configure LLM integration for your voice chatbot.
"""

import os
import sys
import requests
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🤖 Voice Chatbot LLM Integration Setup")
    print("=" * 60)
    print()

def check_env_file():
    """Check if .env file exists"""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please copy env_example.txt to .env first:")
        print("   cp env_example.txt .env")
        return False
    return True

def get_user_choice():
    """Get user's LLM choice"""
    print("Choose your LLM provider:")
    print("1. OpenAI GPT (Recommended - Easy setup)")
    print("2. Anthropic Claude (High quality)")
    print("3. Ollama (Local - Free but requires setup)")
    print("4. Skip LLM setup (Use built-in responses only)")
    print()
    
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        print("Please enter a valid choice (1-4)")

def setup_openai():
    """Setup OpenAI configuration"""
    print("\n🔧 Setting up OpenAI GPT...")
    print("1. Go to https://platform.openai.com/")
    print("2. Create an account and get your API key")
    print("3. Enter your API key below:")
    
    api_key = input("OpenAI API Key: ").strip()
    
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format. OpenAI keys start with 'sk-'")
        return False
    
    # Test the API key
    print("Testing API key...")
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.get('https://api.openai.com/v1/models', headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ API key is valid!")
            return update_env_file('openai', api_key)
        else:
            print(f"❌ API key test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False

def setup_anthropic():
    """Setup Anthropic configuration"""
    print("\n🔧 Setting up Anthropic Claude...")
    print("1. Go to https://console.anthropic.com/")
    print("2. Create an account and get your API key")
    print("3. Enter your API key below:")
    
    api_key = input("Anthropic API Key: ").strip()
    
    if not api_key.startswith('sk-ant-'):
        print("❌ Invalid API key format. Anthropic keys start with 'sk-ant-'")
        return False
    
    # Test the API key
    print("Testing API key...")
    headers = {'x-api-key': api_key, 'Content-Type': 'application/json'}
    try:
        response = requests.get('https://api.anthropic.com/v1/models', headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ API key is valid!")
            return update_env_file('anthropic', api_key)
        else:
            print(f"❌ API key test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False

def setup_ollama():
    """Setup Ollama configuration"""
    print("\n🔧 Setting up Ollama (Local LLM)...")
    print("1. Install Ollama from https://ollama.ai/")
    print("2. Start Ollama: ollama serve")
    print("3. Pull a model: ollama pull llama2")
    print("4. Test connection...")
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                print("✅ Ollama is running!")
                print(f"Available models: {[m['name'] for m in models]}")
                return update_env_file('ollama')
            else:
                print("⚠️  Ollama is running but no models found.")
                print("Run: ollama pull llama2")
                return update_env_file('ollama')
        else:
            print("❌ Ollama is not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Make sure Ollama is installed and running: ollama serve")
        return False

def update_env_file(llm_type, api_key=None):
    """Update .env file with LLM configuration"""
    try:
        # Read current .env file
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Update LLM settings
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('USE_LLM='):
                lines[i] = 'USE_LLM=true\n'
                updated = True
            elif line.startswith('ACTIVE_LLM='):
                lines[i] = f'ACTIVE_LLM={llm_type}\n'
                updated = True
            elif llm_type == 'openai' and line.startswith('OPENAI_API_KEY='):
                lines[i] = f'OPENAI_API_KEY={api_key}\n'
                updated = True
            elif llm_type == 'anthropic' and line.startswith('ANTHROPIC_API_KEY='):
                lines[i] = f'ANTHROPIC_API_KEY={api_key}\n'
                updated = True
        
        # Write updated .env file
        with open('.env', 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Successfully configured {llm_type.upper()}!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def test_integration():
    """Test the LLM integration"""
    print("\n🧪 Testing LLM integration...")
    
    try:
        response = requests.post(
            'http://localhost:5001/api/process-text',
            headers={'Content-Type': 'application/json'},
            json={'text': 'Hello, can you explain what you can do?'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                print("✅ LLM integration is working!")
                print(f"Response: {data['response'][:100]}...")
                return True
            else:
                print("❌ Unexpected response format")
                return False
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        print("Make sure the Flask app is running: python app.py")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check if .env file exists
    if not check_env_file():
        return
    
    # Get user choice
    choice = get_user_choice()
    
    success = False
    if choice == '1':
        success = setup_openai()
    elif choice == '2':
        success = setup_anthropic()
    elif choice == '3':
        success = setup_ollama()
    elif choice == '4':
        print("\n⏭️  Skipping LLM setup. Using built-in responses only.")
        success = True
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Restart your Flask app: python app.py")
        print("2. Test the integration with voice or text input")
        print("3. Check LLM_SETUP.md for advanced configuration")
        
        # Ask if user wants to test
        test = input("\nWould you like to test the integration now? (y/n): ").strip().lower()
        if test == 'y':
            test_integration()
    else:
        print("\n❌ Setup failed. Please check the errors above and try again.")
        print("You can still use the chatbot with built-in responses.")

if __name__ == "__main__":
    main()

