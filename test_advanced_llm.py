#!/usr/bin/env python3
"""
Advanced LLM Test Script
Tests the enhanced LLM integration with various types of queries
"""

import requests
import json
import time
from datetime import datetime

def test_advanced_llm_features():
    """Test advanced LLM features with various query types"""
    
    base_url = "http://localhost:5001"
    
    # Test queries organized by complexity and type
    test_queries = {
        "Basic Questions": [
            "What time is it?",
            "Tell me a joke",
            "How are you today?"
        ],
        "Advanced Knowledge": [
            "Explain quantum computing in simple terms",
            "What are the main differences between machine learning and deep learning?",
            "How does blockchain technology work and what are its applications?",
            "What is the philosophy of existentialism and how does it relate to modern life?",
            "Explain the concept of supply and demand in economics with real-world examples"
        ],
        "Creative Requests": [
            "Write a short story about a robot learning to paint",
            "Create a poem about artificial intelligence",
            "Imagine a world where everyone can fly - what would change?",
            "Design a futuristic city and describe its features"
        ],
        "Complex Analysis": [
            "What are the advantages and disadvantages of remote work?",
            "How has social media impacted human relationships and communication?",
            "What are the environmental impacts of renewable energy vs fossil fuels?",
            "Analyze the role of artificial intelligence in modern healthcare"
        ],
        "Personal & Conversational": [
            "What do you think about the future of education?",
            "How do you feel about the relationship between technology and human creativity?",
            "What's your opinion on the importance of work-life balance?",
            "Can you share your thoughts on the meaning of happiness?"
        ],
        "Problem Solving": [
            "I'm trying to learn a new programming language. What's the best approach?",
            "How can I improve my productivity while working from home?",
            "What strategies can help me manage stress and anxiety?",
            "I want to start a business but don't know where to begin. Can you help?"
        ],
        "Educational": [
            "Teach me about the history of the internet",
            "How do neural networks work in artificial intelligence?",
            "What are the key principles of sustainable development?",
            "Explain the concept of emotional intelligence and its importance"
        ]
    }
    
    print("🚀 Testing Advanced LLM Integration")
    print("=" * 50)
    
    # Test each category
    for category, queries in test_queries.items():
        print(f"\n📚 {category}")
        print("-" * 30)
        
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. Query: {query}")
            print("Response:")
            
            try:
                # Send the query
                response = requests.post(
                    f"{base_url}/api/process-text",
                    json={"text": query},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', 'No response received')
                    
                    # Print the response with formatting
                    print(f"   {response_text}")
                    
                    # Show intent and confidence
                    intent = result.get('intent', 'unknown')
                    confidence = result.get('confidence', 0)
                    print(f"   [Intent: {intent}, Confidence: {confidence:.2f}]")
                    
                else:
                    print(f"   ❌ Error: HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Network Error: {e}")
            except Exception as e:
                print(f"   ❌ Unexpected Error: {e}")
            
            # Small delay between requests
            time.sleep(1)
    
    print("\n" + "=" * 50)
    print("✅ Advanced LLM Testing Complete!")

def test_conversation_flow():
    """Test conversation flow and context awareness"""
    
    base_url = "http://localhost:5001"
    
    conversation_flow = [
        "Hello! I'm interested in learning about artificial intelligence.",
        "What are the main types of AI?",
        "Can you explain machine learning in more detail?",
        "How does deep learning differ from traditional machine learning?",
        "What are some real-world applications of deep learning?",
        "Do you think AI will replace human jobs?",
        "What should I study if I want to work in AI?",
        "Thank you for the detailed explanations!"
    ]
    
    print("\n💬 Testing Conversation Flow & Context Awareness")
    print("=" * 50)
    
    for i, message in enumerate(conversation_flow, 1):
        print(f"\n{i}. User: {message}")
        
        try:
            response = requests.post(
                f"{base_url}/api/process-text",
                json={"text": message},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', 'No response received')
                
                print(f"   Assistant: {response_text}")
                
                # Show if LLM was used
                intent = result.get('intent', 'unknown')
                print(f"   [Intent: {intent}]")
                
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Network Error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected Error: {e}")
        
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("✅ Conversation Flow Testing Complete!")

def test_llm_configuration():
    """Test LLM configuration and status"""
    
    base_url = "http://localhost:5001"
    
    print("\n⚙️ Testing LLM Configuration")
    print("=" * 50)
    
    try:
        # Test features endpoint
        response = requests.get(f"{base_url}/api/features")
        if response.status_code == 200:
            features = response.json()
            print("Available Features:")
            for feature in features:
                print(f"   • {feature}")
        
        # Test status endpoint
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"\nSystem Status: {status.get('status', 'unknown')}")
            print(f"LLM Enabled: {status.get('llm_enabled', False)}")
            print(f"Active LLM: {status.get('active_llm', 'none')}")
        
    except Exception as e:
        print(f"❌ Configuration Test Error: {e}")

def main():
    """Main test function"""
    print("🧠 Advanced LLM Integration Test Suite")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test LLM configuration first
    test_llm_configuration()
    
    # Test conversation flow
    test_conversation_flow()
    
    # Test advanced features
    test_advanced_llm_features()
    
    print(f"\n🏁 All tests completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
