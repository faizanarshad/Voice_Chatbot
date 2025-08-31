#!/usr/bin/env python3
"""
Direct LLM Test Script
Tests the LLM integration directly without going through the web API
"""

import os
import sys
from nlp_engine import LLMIntegration

def test_llm_directly():
    """Test LLM integration directly"""
    
    print("🧠 Testing LLM Integration Directly")
    print("=" * 50)
    
    # Initialize LLM
    llm = LLMIntegration()
    
    print(f"Active LLM: {llm.active_llm}")
    print(f"OpenAI API Key: {'Set' if llm.openai_api_key else 'Not Set'}")
    print(f"Anthropic API Key: {'Set' if llm.anthropic_api_key else 'Not Set'}")
    print(f"Ollama Base URL: {llm.ollama_base_url}")
    
    # Test queries
    test_queries = [
        "Hello, how are you today?",
        "What is your opinion on artificial intelligence?",
        "Write a short story about a robot learning to paint",
        "Explain quantum computing in simple terms"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("Response:")
        
        try:
            response = llm.generate_response(query)
            print(f"   {response}")
            
            # Check if it's a fallback response
            if any(fallback in response for fallback in [
                "I understand you said:", "Thanks for your message:", 
                "I received:", "Your message:"
            ]):
                print("   ⚠️  This is a fallback response - LLM API may not be working")
            else:
                print("   ✅ LLM response received successfully")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Direct LLM Testing Complete!")

if __name__ == "__main__":
    test_llm_directly()
