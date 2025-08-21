#!/usr/bin/env python3
"""
Quick LLM Enablement Script
This script helps you quickly enable LLM integration for advanced text chat.
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🤖 Advanced Text Chat LLM Setup")
    print("=" * 60)
    print()

def check_env_file():
    """Check if .env file exists"""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Creating .env file from template...")
        try:
            with open('env_example.txt', 'r') as template:
                with open('.env', 'w') as env_file:
                    env_file.write(template.read())
            print("✅ .env file created successfully!")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    return True

def enable_llm():
    """Enable LLM integration"""
    env_path = Path('.env')
    
    # Read current .env content
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Update LLM settings
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('USE_LLM='):
            updated_lines.append('USE_LLM=true')
        elif line.startswith('ACTIVE_LLM='):
            updated_lines.append('ACTIVE_LLM=openai')
        else:
            updated_lines.append(line)
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ LLM integration enabled!")
    print("   - USE_LLM=true")
    print("   - ACTIVE_LLM=openai")

def get_api_key():
    """Get API key from user"""
    print("\n🔑 To use advanced text chat, you need an API key:")
    print("1. Get a free API key from OpenAI: https://platform.openai.com/api-keys")
    print("2. Or use Anthropic Claude: https://console.anthropic.com/")
    print("3. Or use local Ollama (free): https://ollama.ai/")
    
    choice = input("\nChoose your LLM provider (1=OpenAI, 2=Anthropic, 3=Ollama, 4=Skip for now): ").strip()
    
    if choice == '1':
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            update_env_file('OPENAI_API_KEY', api_key)
            update_env_file('ACTIVE_LLM', 'openai')
            print("✅ OpenAI API key configured!")
        else:
            print("⚠️  No API key provided. LLM will use fallback responses.")
    
    elif choice == '2':
        api_key = input("Enter your Anthropic API key: ").strip()
        if api_key:
            update_env_file('ANTHROPIC_API_KEY', api_key)
            update_env_file('ACTIVE_LLM', 'anthropic')
            print("✅ Anthropic API key configured!")
        else:
            print("⚠️  No API key provided. LLM will use fallback responses.")
    
    elif choice == '3':
        print("✅ Ollama selected! Make sure Ollama is running locally.")
        update_env_file('ACTIVE_LLM', 'ollama')
    
    else:
        print("⚠️  Skipping API key setup. LLM will use fallback responses.")

def update_env_file(key, value):
    """Update a key in .env file"""
    env_path = Path('.env')
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    updated_lines = []
    key_updated = False
    
    for line in lines:
        if line.startswith(f'{key}='):
            updated_lines.append(f'{key}={value}')
            key_updated = True
        else:
            updated_lines.append(line)
    
    if not key_updated:
        updated_lines.append(f'{key}={value}')
    
    with open(env_path, 'w') as f:
        f.write('\n'.join(updated_lines))

def main():
    """Main setup function"""
    print_banner()
    
    if not check_env_file():
        return
    
    enable_llm()
    get_api_key()
    
    print("\n🎉 Setup complete!")
    print("\n📝 Next steps:")
    print("1. Restart your voice chatbot: python app.py")
    print("2. Try advanced questions like:")
    print("   - 'Explain quantum computing in simple terms'")
    print("   - 'What are the benefits of renewable energy?'")
    print("   - 'How does machine learning work?'")
    print("   - 'Compare different programming languages'")
    print("\n💡 The chatbot will now provide advanced, intelligent responses!")

if __name__ == "__main__":
    main()
