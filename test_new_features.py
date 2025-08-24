#!/usr/bin/env python3
"""
Test Script for Enhanced Voice Chatbot Features
Tests all the new capabilities added to the chatbot
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_feature(feature_name, test_queries):
    """Test a specific feature with multiple queries"""
    print(f"\n🎯 **Testing {feature_name.upper()} Feature**")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n📝 **Query**: {query}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/test-feature/{feature_name}",
                json={"text": query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ **Intent**: {result.get('intent')}")
                print(f"🎯 **Confidence**: {result.get('confidence'):.2f}")
                print(f"💬 **Response**: {result.get('response')[:200]}...")
            else:
                print(f"❌ **Error**: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ **Exception**: {e}")
        
        time.sleep(1)  # Small delay between requests

def main():
    """Main test function"""
    print("🚀 **Enhanced Voice Chatbot Feature Testing**")
    print("=" * 60)
    
    # Test Music Control Feature
    music_queries = [
        "Play some music",
        "Pause the current song",
        "Volume up",
        "Next track please",
        "Play rock music"
    ]
    test_feature("music_control", music_queries)
    
    # Test Calendar Feature
    calendar_queries = [
        "Schedule a meeting tomorrow",
        "What's on my calendar today?",
        "Set a reminder to call mom",
        "Add lunch meeting at 1 PM"
    ]
    test_feature("calendar", calendar_queries)
    
    # Test Weather Detailed Feature
    weather_queries = [
        "Show me the 5-day forecast",
        "What's the UV index today?",
        "Check air quality in my area",
        "Are there any storm warnings?"
    ]
    test_feature("weather_detailed", weather_queries)
    
    # Test News Category Feature
    news_queries = [
        "Show me world news",
        "What's the latest in technology?",
        "Give me sports headlines",
        "Business news updates"
    ]
    test_feature("news_category", news_queries)
    
    # Test Advanced Calculator Feature
    calc_queries = [
        "Calculate 25% of 200",
        "What's the square root of 144?",
        "Solve 2x + 5 = 15",
        "Convert 100 Fahrenheit to Celsius"
    ]
    test_feature("calculator_advanced", calc_queries)
    
    # Test Notes Feature
    notes_queries = [
        "Create a note for my shopping list",
        "Save this idea for later",
        "Write down my meeting notes",
        "Find my password note"
    ]
    test_feature("notes", notes_queries)
    
    # Test Tasks Feature
    tasks_queries = [
        "Add buy groceries to my task list",
        "Mark meeting preparation as complete",
        "Show my todo list",
        "Set priority for project deadline"
    ]
    test_feature("tasks", tasks_queries)
    
    # Test Web Search Feature
    search_queries = [
        "Search for best restaurants nearby",
        "Find information about quantum computing",
        "Look up the latest iPhone reviews",
        "Research machine learning algorithms"
    ]
    test_feature("web_search", search_queries)
    
    print("\n🎉 **Feature Testing Complete!**")
    print("=" * 60)

if __name__ == "__main__":
    main()
