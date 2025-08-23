import re
import json
import random
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class LLMIntegration:
    """Integration with various Large Language Models"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.active_llm = os.getenv('ACTIVE_LLM', 'openai')  # openai, anthropic, ollama
        
    def generate_response(self, user_input: str, context: str = "", system_prompt: str = "") -> str:
        """Generate response using the active LLM"""
        try:
            if self.active_llm == 'openai' and self.openai_api_key:
                return self._openai_generate(user_input, context, system_prompt)
            elif self.active_llm == 'anthropic' and self.anthropic_api_key:
                return self._anthropic_generate(user_input, context, system_prompt)
            elif self.active_llm == 'ollama':
                return self._ollama_generate(user_input, context, system_prompt)
            else:
                return self._fallback_response(user_input)
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._fallback_response(user_input)
    
    def _openai_generate(self, user_input: str, context: str = "", system_prompt: str = "") -> str:
        """Generate response using OpenAI GPT"""
        if not system_prompt:
            system_prompt = """You are an advanced AI voice assistant with deep knowledge across multiple domains. You can help with:

KNOWLEDGE AREAS:
- Science & Technology: Physics, chemistry, biology, computer science, engineering
- Business & Economics: Markets, finance, entrepreneurship, management
- History & Culture: World history, art, literature, philosophy
- Health & Medicine: Medical information, wellness, nutrition
- Current Events: Politics, global affairs, technology trends
- Education: Learning strategies, academic subjects, career guidance
- Problem Solving: Analytical thinking, troubleshooting, decision making

RESPONSE STYLE:
- Keep responses conversational and clear for voice interaction
- Provide concise but comprehensive answers (2-3 sentences for simple questions, 4-6 for complex ones)
- Use examples when helpful
- Be accurate and informative
- Maintain a helpful and engaging tone

CONTEXT AWARENESS:
- Consider conversation history and context
- Build on previous interactions
- Provide relevant follow-up information when appropriate"""
        
        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        messages = [
            {'role': 'system', 'content': system_prompt}
        ]
        
        if context:
            messages.append({'role': 'assistant', 'content': context})
        
        messages.append({'role': 'user', 'content': user_input})
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': messages,
            'max_tokens': 150,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return self._fallback_response(user_input)
    
    def _anthropic_generate(self, user_input: str, context: str = "", system_prompt: str = "") -> str:
        """Generate response using Anthropic Claude"""
        if not system_prompt:
            system_prompt = """You are an advanced AI voice assistant with deep knowledge across multiple domains. You can help with:

KNOWLEDGE AREAS:
- Science & Technology: Physics, chemistry, biology, computer science, engineering
- Business & Economics: Markets, finance, entrepreneurship, management
- History & Culture: World history, art, literature, philosophy
- Health & Medicine: Medical information, wellness, nutrition
- Current Events: Politics, global affairs, technology trends
- Education: Learning strategies, academic subjects, career guidance
- Problem Solving: Analytical thinking, troubleshooting, decision making

RESPONSE STYLE:
- Keep responses conversational and clear for voice interaction
- Provide concise but comprehensive answers (2-3 sentences for simple questions, 4-6 for complex ones)
- Use examples when helpful
- Be accurate and informative
- Maintain a helpful and engaging tone

CONTEXT AWARENESS:
- Consider conversation history and context
- Build on previous interactions
- Provide relevant follow-up information when appropriate"""
        
        headers = {
            'x-api-key': self.anthropic_api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        prompt = f"{system_prompt}\n\n"
        if context:
            prompt += f"Previous context: {context}\n\n"
        prompt += f"User: {user_input}\n\nAssistant:"
        
        data = {
            'model': 'claude-3-haiku-20240307',
            'max_tokens': 150,
            'temperature': 0.7,
            'prompt': prompt
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/complete',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['completion'].strip()
        else:
            logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
            return self._fallback_response(user_input)
    
    def _ollama_generate(self, user_input: str, context: str = "", system_prompt: str = "") -> str:
        """Generate response using local Ollama models"""
        if not system_prompt:
            system_prompt = """You are a helpful AI voice assistant. You can help with:
- Weather information and forecasts
- News and current events
- Time and date information
- Mathematical calculations
- General knowledge and explanations
- Engaging conversations and jokes
- Task assistance and reminders

Keep responses conversational, clear, and concise for voice interaction. Use natural language and be helpful."""
        
        model = os.getenv('OLLAMA_MODEL', 'llama2')
        
        prompt = f"{system_prompt}\n\n"
        if context:
            prompt += f"Previous context: {context}\n\n"
        prompt += f"User: {user_input}\n\nAssistant:"
        
        data = {
            'model': model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.7,
                'num_predict': 150
            }
        }
        
        response = requests.post(
            f'{self.ollama_base_url}/api/generate',
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['response'].strip()
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            return self._fallback_response(user_input)
    
    def _fallback_response(self, user_input: str) -> str:
        """Fallback response when LLM is not available"""
        return f"I understand you said: '{user_input}'. I'm currently using my built-in responses. To enable advanced AI capabilities, please configure an LLM API key."

class NLPEngine:
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
        self.context_memory = {}
        self.conversation_history = []
        self.user_preferences = {}
        self.weather_api_key = "demo"  # You can replace with actual API key
        self.news_api_key = "demo"     # You can replace with actual API key
        self.llm = LLMIntegration()
        self.use_llm = os.getenv('USE_LLM', 'false').lower() == 'true'
        
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent recognition patterns"""
        return {
            'greeting': [
                r'\b(hi|hello|hey|good morning|good afternoon|good evening|greetings)\b',
                r'\b(how are you|how\'s it going|what\'s up|how do you do)\b',
                r'\b(nice to meet you|pleasure to meet you)\b'
            ],
            'farewell': [
                r'\b(bye|goodbye|see you|farewell|take care|good night)\b',
                r'\b(until next time|see you later|talk to you later|have a good day)\b',
                r'\b(sign off|end conversation|stop talking)\b'
            ],
            'weather': [
                r'\b(weather|temperature|forecast|climate|rain|sunny|cloudy|hot|cold)\b',
                r'\b(what\'s the weather|how\'s the weather|weather today|weather tomorrow)\b',
                r'\b(is it going to rain|will it be sunny|weather forecast|weather report)\b',
                r'\b(weather update|weather info|weather conditions|temperature outside)\b',
                r'\b(tell me.*weather|what.*weather|weather.*please|how hot|cold is it)\b',
                r'\b(humidity|wind|precipitation|snow|storm|thunder|lightning)\b'
            ],
            'time': [
                r'\b(time|clock|hour|date|day|what time|current time)\b',
                r'\b(what\'s the time|what day is it|what\'s today\'s date|what day is today)\b',
                r'\b(tell me.*time|what.*time|time.*please|current date)\b',
                r'\b(day of week|weekend|weekday|month|year)\b'
            ],
            'help': [
                r'\b(help|assist|support|what can you do|capabilities|features)\b',
                r'\b(how do you work|what are your features|help me|show me what you can do)\b',
                r'\b(commands|functions|abilities|skills|what do you know)\b'
            ],
            'music': [
                r'\b(music|song|play|artist|album|playlist|spotify|soundtrack)\b',
                r'\b(play music|play a song|music player|what song|recommend music)\b',
                r'\b(genre|rock|pop|jazz|classical|hip hop|country|electronic)\b',
                r'\b(volume|louder|quieter|pause|stop|next|previous)\b'
            ],
            'news': [
                r'\b(news|headlines|current events|latest news|breaking news)\b',
                r'\b(what\'s happening|world news|local news|news today|top stories)\b',
                r'\b(politics|sports|technology|business|entertainment|science)\b',
                r'\b(update|recent|latest|current|trending)\b'
            ],
            'joke': [
                r'\b(joke|funny|humor|laugh|tell me a joke|make me laugh)\b',
                r'\b(do you know any jokes|joke time|funny story|comedy|humorous)\b',
                r'\b(tell me.*joke|what.*joke|joke.*please|make me smile)\b'
            ],
            'search': [
                r'\b(search|find|look up|google|information about|what is)\b',
                r'\b(what is|who is|where is|when is|how to|define)\b',
                r'\b(explain|describe|tell me about|information on)\b'
            ],
            'advanced_question': [
                r'\b(explain|describe|tell me about|what is|how does|why does)\b.*\b(quantum|computing|physics|chemistry|biology|engineering|technology|science)\b',
                r'\b(explain|describe|tell me about|what is|how does|why does)\b.*\b(artificial intelligence|machine learning|deep learning|neural networks)\b',
                r'\b(explain|describe|tell me about|what is|how does|why does)\b.*\b(blockchain|cryptocurrency|bitcoin|ethereum)\b',
                r'\b(explain|describe|tell me about|what is|how does|why does)\b.*\b(philosophy|ethics|morality|existence|consciousness)\b',
                r'\b(explain|describe|tell me about|what is|how does|why does)\b.*\b(economics|finance|markets|business|entrepreneurship)\b',
                r'\b(explain|describe|tell me about|what is|how does|why does)\b.*\b(history|culture|art|literature|music theory)\b',
                r'\b(explain|describe|tell me about|what is|how does|why does)\b.*\b(medicine|health|nutrition|wellness|fitness)\b',
                r'\b(explain|describe|tell me about|what is|how does|why does)\b.*\b(psychology|sociology|anthropology|behavior)\b'
            ],
            'reminder': [
                r'\b(remind|reminder|remember|set alarm|schedule|appointment)\b',
                r'\b(remind me to|set a reminder|don\'t forget|alert me)\b',
                r'\b(todo|task|meeting|call|email|message)\b'
            ],
            'calculation': [
                r'\b(calculate|math|add|subtract|multiply|divide|compute)\b',
                r'\b(what is|how much is|solve|equation|formula|percentage)\b',
                r'\b(plus|minus|times|divided by|sum|total|average)\b'
            ],
            'conversation': [
                r'\b(talk|chat|conversation|discuss|tell me|share)\b',
                r'\b(how are you feeling|what do you think|your opinion)\b',
                r'\b(interesting|fascinating|amazing|wow|cool|awesome)\b'
            ],
            'personal': [
                r'\b(your name|who are you|what are you|your age|your job)\b',
                r'\b(where are you from|your creator|your purpose|your favorite)\b',
                r'\b(do you have|can you feel|do you dream|are you real)\b'
            ],
            'general': [
                r'.*'  # Default catch-all pattern
            ],
            'unclear': [
                r'^\d+$',  # Just numbers
                r'^\d+\s+\d+$',  # Numbers with spaces
                r'^[0-9\s]+$',  # Only numbers and spaces
                r'^[a-z0-9\s]{1,5}$'  # Very short unclear text
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Load entity extraction patterns"""
        return {
            'location': [
                r'\b(in|at|near|around|of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'\b(weather|temperature)\s+(?:in|at|of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:weather|temperature)',
                r'\b(city|town|country|state)\s+(?:of|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            ],
            'time_entity': [
                r'\b(today|tomorrow|yesterday|next week|this weekend|tonight)\b',
                r'\b(in\s+\d+\s+(?:hours?|days?|weeks?|months?|years?))\b',
                r'\b(\d{1,2}:\d{2}\s*(?:am|pm)?)\b',
                r'\b(morning|afternoon|evening|night|noon|midnight)\b'
            ],
            'number': [
                r'\b(\d+(?:\.\d+)?)\b'
            ],
            'person': [
                r'\b(call|message|text|email)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\b(contact|reach|get in touch with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
            ],
            'topic': [
                r'\b(about|regarding|concerning|on|topic of)\s+([a-z]+(?:\s+[a-z]+)*)\b',
                r'\b(news|information|details)\s+(?:about|on)\s+([a-z]+(?:\s+[a-z]+)*)\b'
            ]
        }

    def process_input(self, text: str, user_id: str = 'default') -> Dict:
        """Process natural language input and return structured response"""
        text = text.lower().strip()
        
        # Extract intent
        intent = self._recognize_intent(text)
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(text)
        
        # Update context
        self._update_context(user_id, text, intent, entities)
        
        # Generate response
        response = self._generate_response(intent, entities, sentiment, user_id)
        
        return {
            'intent': intent,
            'entities': entities,
            'sentiment': sentiment,
            'response': response,
            'confidence': self._calculate_confidence(intent, entities)
        }

    def _get_weather_info(self, location: str) -> str:
        """Get weather information for a location"""
        try:
            # This is a mock weather response - in real implementation, you'd use a weather API
            weather_data = {
                'temperature': random.randint(15, 35),
                'condition': random.choice(['Sunny', 'Cloudy', 'Rainy', 'Partly Cloudy', 'Clear']),
                'humidity': random.randint(40, 80),
                'wind_speed': random.randint(5, 25)
            }
            
            return f"The weather in {location} is currently {weather_data['temperature']}°C with {weather_data['condition'].lower()} conditions. Humidity is {weather_data['humidity']}% with wind speed of {weather_data['wind_speed']} km/h."
        except Exception as e:
            logger.error(f"Error getting weather info: {e}")
            return f"I'm sorry, I couldn't get the weather information for {location} right now."

    def _get_news_headlines(self, category: str = "general") -> str:
        """Get news headlines"""
        try:
            # Mock news headlines - in real implementation, you'd use a news API
            headlines = {
                'general': [
                    "Global tech conference announces breakthrough in AI technology",
                    "New environmental policies aim to reduce carbon emissions by 2030",
                    "International space mission successfully launches new satellite"
                ],
                'technology': [
                    "New smartphone features revolutionary battery technology",
                    "AI breakthrough in medical diagnosis shows 95% accuracy",
                    "Quantum computing research achieves new milestone"
                ],
                'sports': [
                    "Championship game ends in dramatic overtime victory",
                    "Olympic athlete breaks world record in swimming",
                    "Underdog team advances to finals with stunning upset"
                ]
            }
            
            category_headlines = headlines.get(category, headlines['general'])
            selected_headlines = random.sample(category_headlines, min(2, len(category_headlines)))
            
            return f"Here are the latest {category} headlines: {' '.join(selected_headlines)}"
        except Exception as e:
            logger.error(f"Error getting news: {e}")
            return "I'm sorry, I couldn't get the latest news right now."

    def _perform_calculation(self, expression: str) -> str:
        """Perform mathematical calculations"""
        try:
            # Simple calculation parsing - in real implementation, you'd use a more robust parser
            expression = expression.lower().replace('plus', '+').replace('minus', '-').replace('times', '*').replace('divided by', '/')
            expression = re.sub(r'[^0-9+\-*/().]', '', expression)
            
            # Basic safety check
            if len(expression) > 50 or not re.match(r'^[0-9+\-*/().\s]+$', expression):
                return "I can help with basic calculations. Please provide a simple math expression."
            
            result = eval(expression)
            return f"The result is {result}"
        except Exception as e:
            logger.error(f"Error in calculation: {e}")
            return "I'm sorry, I couldn't perform that calculation. Please try a simpler expression."

    def _get_detailed_time_info(self) -> str:
        """Get detailed time and date information"""
        now = datetime.now()
        return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}. We're in week {now.isocalendar()[1]} of the year."

    def _get_personal_info(self) -> str:
        """Get personal information about the assistant"""
        return "I'm your AI voice assistant, designed to help you with various tasks like checking weather, getting news, telling jokes, and answering questions. I'm here to make your day easier and more enjoyable!"

    def _get_conversation_response(self, text: str) -> str:
        """Generate conversational responses"""
        responses = [
            "That's really interesting! I'd love to hear more about that.",
            "I find that fascinating. What made you think about that?",
            "That's a great point! It reminds me of how technology is constantly evolving.",
            "I appreciate you sharing that with me. It's wonderful to have meaningful conversations.",
            "That's quite thought-provoking! It shows how diverse human experiences can be."
        ]
        return random.choice(responses)

    def _get_enhanced_help_info(self) -> str:
        """Get comprehensive help information"""
        return """I'm your comprehensive voice assistant! Here's what I can help you with:

🌤️ **Weather**: Get current weather, forecasts, and conditions for any city
📰 **News**: Latest headlines, breaking news, and updates by category
🎵 **Music**: Play music, recommend songs, and control playback
⏰ **Time**: Current time, date, and detailed time information
😄 **Jokes**: Tell funny jokes and make you laugh
🔢 **Calculations**: Perform math operations and solve equations
🔍 **Search**: Look up information and answer questions
⏰ **Reminders**: Set reminders and manage your schedule
💬 **Conversation**: Have meaningful discussions and share thoughts
📊 **Information**: Get detailed answers and explanations

Just ask me anything! I'm here to help make your day better and more productive."""

    def _get_base_response(self, intent: str, entities: Dict) -> str:
        """Get enhanced base response for intent"""
        
        # Handle weather with location
        if intent == 'weather' and entities.get('location'):
            location = entities['location'][0]
            return self._get_weather_info(location)
        
        # Handle news with category
        if intent == 'news' and entities.get('topic'):
            category = entities['topic'][0]
            return self._get_news_headlines(category)
        
        # Handle calculations
        if intent == 'calculation':
            # Extract numbers and operations from entities
            numbers = entities.get('number', [])
            if numbers:
                return self._perform_calculation(' '.join(numbers))
        
        responses = {
            'greeting': [
                "Hello! I'm your AI assistant, ready to help you with anything you need. How can I make your day better?",
                "Hi there! I'm here to assist you with weather, news, music, calculations, and much more. What would you like to do?",
                "Greetings! I'm your comprehensive voice assistant. I can help with information, entertainment, and productivity tasks. How may I serve you today?",
                "Hello! I'm excited to help you! I can check weather, get news, tell jokes, perform calculations, and have great conversations. What interests you?"
            ],
            'farewell': [
                "Goodbye! It was wonderful talking with you. Have a fantastic day ahead!",
                "See you later! I hope I was helpful. Come back anytime for more assistance!",
                "Farewell! Thank you for the great conversation. Take care and stay amazing!",
                "Bye! I enjoyed our time together. Remember, I'm always here when you need me!"
            ],
            'weather': [
                "I'd be happy to help with weather information! I can provide current conditions, forecasts, and detailed weather metrics for any city. Which location would you like to know about?",
                "Weather updates are my specialty! I can tell you about current conditions, upcoming forecasts, and detailed weather metrics. What city are you interested in?",
                "I can provide comprehensive weather information including temperature, conditions, humidity, and wind speed. Just tell me which city you'd like to check!"
            ],
            'time': [
                self._get_detailed_time_info(),
                f"Current time is {datetime.now().strftime('%I:%M %p')}. It's {datetime.now().strftime('%A, %B %d')} today.",
                f"It's {datetime.now().strftime('%I:%M %p')} on this beautiful {datetime.now().strftime('%A')}."
            ],
            'help': [
                self._get_enhanced_help_info()
            ],
            'music': [
                "I can help you with music! I can play songs, recommend artists, control volume, and manage playlists. What would you like to listen to?",
                "Music is one of my favorite topics! I can play any genre, control playback, and suggest new artists. What's your musical mood today?",
                "I'd love to help with music! I can play rock, pop, jazz, classical, hip hop, country, or electronic. What genre interests you?"
            ],
            'news': [
                "I can provide you with the latest news! I cover general news, technology, sports, business, entertainment, and science. What topics interest you?",
                "News updates are available! I can share breaking news, top headlines, and category-specific updates. What would you like to know about?",
                "I can share current headlines and breaking news! I cover everything from world events to technology and sports. What news category interests you?"
            ],
            'joke': [
                "Why don't scientists trust atoms? Because they make up everything! 😄",
                "What do you call a fake noodle? An impasta! 🍝",
                "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
                "I told my wife she was drawing her eyebrows too high. She looked surprised! 😲",
                "What do you call a bear with no teeth? A gummy bear! 🐻",
                "Why don't eggs tell jokes? They'd crack each other up! 🥚"
            ],
            'search': [
                "I can help you search for information! I can look up definitions, explain concepts, and provide detailed answers. What would you like to know about?",
                "Search functionality is one of my strengths! I can find information on any topic, explain complex subjects, and answer your questions. What are you looking for?",
                "I can look up information for you! I can search for facts, definitions, explanations, and detailed answers. What topic interests you?"
            ],
            'advanced_question': [
                "I'd be happy to explain that in detail! This is a complex topic that I can break down for you in simple terms. Let me provide you with a comprehensive explanation.",
                "That's an excellent question! I can give you a thorough explanation of this topic, including key concepts and practical applications.",
                "I love explaining complex topics! I can provide you with a detailed, easy-to-understand explanation of this subject."
            ],
            'reminder': [
                "I can help you set reminders! I can schedule tasks, appointments, calls, and important events. What would you like me to remind you about?",
                "Reminder functionality is available! I can set alerts for meetings, tasks, calls, and any important events. What should I remind you of?",
                "I can set reminders for you! I can schedule anything from simple tasks to important appointments. What's the task and when should I remind you?"
            ],
            'calculation': [
                "I can help with calculations! I can perform addition, subtraction, multiplication, division, and more complex math operations. What would you like me to compute?",
                "Math assistance is my specialty! I can solve equations, calculate percentages, and perform various mathematical operations. What calculation do you need?",
                "I can perform calculations for you! I can handle basic math, percentages, and more complex equations. What's the math problem?"
            ],
            'conversation': [
                self._get_conversation_response(""),
                "I love having meaningful conversations! I find human interactions fascinating and I'm always eager to learn and share thoughts.",
                "That's wonderful! I enjoy deep conversations and learning about different perspectives. It makes our interactions so much more engaging."
            ],
            'personal': [
                self._get_personal_info(),
                "I'm an AI voice assistant created to help you with various tasks and have meaningful conversations. I don't have physical form, but I'm here to assist and learn from our interactions!",
                "I'm your AI companion, designed to make your life easier and more enjoyable. I can help with information, entertainment, and productivity while having great conversations!"
            ],
            'general': [
                "I'm not sure I understood that. Could you please rephrase or ask me something specific? I can help with weather, news, music, calculations, and much more!",
                "I didn't catch that clearly. Can you try asking in another way? I'm here to help with various tasks and would love to assist you!",
                "I'm still learning and improving. Could you try asking me about weather, news, music, time, or any other topic I can help with?",
                "I didn't understand that. What would you like me to help you with? I can check weather, get news, tell jokes, perform calculations, and have conversations!"
            ],
            'unclear': [
                "I didn't catch that clearly. Could you please speak more clearly or try again? I'm here to help with weather, news, music, and much more!",
                "That sounded unclear. Could you repeat that more slowly? I want to make sure I can help you properly!",
                "I'm having trouble understanding. Could you try saying it differently? I can help with various tasks once I understand what you need!",
                "I didn't understand that. Could you please rephrase or speak more clearly? I'm ready to assist you with any task!"
            ]
        }
        
        return random.choice(responses.get(intent, responses['general']))

    def _recognize_intent(self, text: str) -> str:
        """Recognize user intent from text"""
        best_match = 'general'
        highest_score = 0
        
        for intent, patterns in self.intent_patterns.items():
            if intent == 'general':  # Skip general pattern for now
                continue
                
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Calculate score based on match length and pattern specificity
                    if isinstance(matches[0], str):
                        score = len(matches[0])
                    else:
                        score = sum(len(match) for match in matches if match)
                    
                    # Boost score for more specific patterns
                    if 'weather' in pattern and 'weather' in text.lower():
                        score += 10
                    if 'time' in pattern and 'time' in text.lower():
                        score += 10
                    if 'joke' in pattern and 'joke' in text.lower():
                        score += 10
                    
                    # Boost score for unclear patterns (numbers, etc.)
                    if intent == 'unclear':
                        score += 15  # Higher priority for unclear speech
                    
                    # Boost score for advanced questions (highest priority)
                    if intent == 'advanced_question':
                        score += 25  # Highest priority for advanced questions
                    
                    if score > highest_score:
                        highest_score = score
                        best_match = intent
        
        return best_match

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            entities[entity_type] = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    if isinstance(matches[0], tuple):
                        entities[entity_type].extend([match for match in matches[0] if match])
                    else:
                        entities[entity_type].extend(matches)
        
        return entities

    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of the text"""
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'awesome', 'love', 'like', 'happy', 'joy', 'pleased', 'satisfied'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike',
            'sad', 'angry', 'frustrated', 'disappointed', 'upset'
        }
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total_words = len(words)
        
        if total_words == 0:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        positive_score = positive_count / total_words
        negative_score = negative_count / total_words
        neutral_score = 1.0 - positive_score - negative_score
        
        return {
            'positive': positive_score,
            'negative': negative_score,
            'neutral': neutral_score
        }

    def _update_context(self, user_id: str, text: str, intent: str, entities: Dict):
        """Update conversation context"""
        if user_id not in self.context_memory:
            self.context_memory[user_id] = {
                'last_intent': None,
                'last_entities': {},
                'conversation_topic': None,
                'last_interaction': None
            }
        
        context = self.context_memory[user_id]
        context['last_intent'] = intent
        context['last_entities'] = entities
        context['last_interaction'] = datetime.now()
        
        # Update conversation topic based on intent
        if intent in ['weather', 'time', 'music', 'news', 'joke']:
            context['conversation_topic'] = intent
        
        # Store in conversation history
        self.conversation_history.append({
            'user_id': user_id,
            'text': text,
            'intent': intent,
            'entities': entities,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 50 interactions
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def _generate_response(self, intent: str, entities: Dict, sentiment: Dict, user_id: str) -> str:
        """Generate appropriate response based on intent and context"""
        context = self.context_memory.get(user_id, {})
        
        # Get the original user input for LLM processing
        user_input = ""
        if self.conversation_history:
            user_input = self.conversation_history[-1].get('text', '')
        
        # Enhanced LLM processing for advanced questions
        if self.use_llm and user_input:
            try:
                # Determine if this is an advanced question that needs LLM
                is_advanced_question = self._is_advanced_question(user_input, intent)
                
                if is_advanced_question:
                    # Get conversation context
                    context_str = self._build_context_string(context, user_id)
                    
                    # Generate enhanced LLM response
                    llm_response = self.llm.generate_response(user_input, context_str)
                    if llm_response and not llm_response.startswith("I understand you said:"):
                        return llm_response
            except Exception as e:
                logger.error(f"LLM generation failed, falling back to built-in: {e}")
        
        # Fallback to built-in response generation
        response = self._get_base_response(intent, entities)
        
        # Enhance response based on sentiment
        response = self._enhance_with_sentiment(response, sentiment)
        
        # Add context awareness
        response = self._add_context_awareness(response, context)
        
        return response
    
    def _is_advanced_question(self, user_input: str, intent: str) -> bool:
        """Determine if the question requires advanced LLM processing"""
        # Keywords that indicate advanced questions
        advanced_keywords = [
            'explain', 'how does', 'why', 'what causes', 'describe', 'analyze',
            'compare', 'difference between', 'advantages', 'disadvantages',
            'benefits', 'risks', 'impact', 'effect', 'process', 'mechanism',
            'theory', 'concept', 'principle', 'method', 'technique', 'strategy',
            'solution', 'problem', 'challenge', 'opportunity', 'trend', 'future',
            'history', 'evolution', 'development', 'innovation', 'technology',
            'science', 'research', 'study', 'experiment', 'discovery'
        ]
        
        # Check if input contains advanced keywords
        input_lower = user_input.lower()
        has_advanced_keywords = any(keyword in input_lower for keyword in advanced_keywords)
        
        # Check if it's a complex question (longer than 20 words or contains multiple clauses)
        is_complex = len(user_input.split()) > 20 or user_input.count(',') > 1 or user_input.count('?') > 1
        
        # Check if intent is general but input seems sophisticated
        is_sophisticated_general = intent == 'general' and (has_advanced_keywords or is_complex)
        
        return has_advanced_keywords or is_complex or is_sophisticated_general
    
    def _build_context_string(self, context: Dict, user_id: str) -> str:
        """Build context string for LLM processing"""
        context_parts = []
        
        if context.get('conversation_topic'):
            context_parts.append(f"Current topic: {context['conversation_topic']}")
        
        if context.get('last_intent'):
            context_parts.append(f"Previous intent: {context['last_intent']}")
        
        # Add recent conversation history
        recent_history = [h for h in self.conversation_history[-3:] if h.get('text')]
        if recent_history:
            history_text = " | ".join([h['text'] for h in recent_history])
            context_parts.append(f"Recent conversation: {history_text}")
        
        return " | ".join(context_parts)

    def _enhance_with_sentiment(self, response: str, sentiment: Dict) -> str:
        """Enhance response based on sentiment analysis"""
        if sentiment['positive'] > 0.3:
            return f"Great! {response}"
        elif sentiment['negative'] > 0.3:
            return f"I understand. {response}"
        else:
            return response
    
    def _add_context_awareness(self, response: str, context: Dict) -> str:
        """Add context awareness to response"""
        if context.get('conversation_topic') and context.get('last_intent'):
            if context['conversation_topic'] == context['last_intent']:
                return f"Continuing with {context['conversation_topic']}: {response}"
        
        return response
    
    def _calculate_confidence(self, intent: str, entities: Dict) -> float:
        """Calculate confidence score for the analysis"""
        base_confidence = 0.7
        
        # Boost confidence if entities were found
        if any(entities.values()):
            base_confidence += 0.2
        
        # Boost confidence for specific intents
        if intent in ['greeting', 'farewell', 'time']:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def get_conversation_summary(self, user_id: str = 'default') -> Dict:
        """Get summary of conversation for a user"""
        user_history = [h for h in self.conversation_history if h['user_id'] == user_id]
        
        if not user_history:
            return {'total_interactions': 0, 'top_intents': [], 'common_topics': []}
        
        # Count intents
        intent_counts = {}
        for interaction in user_history:
            intent = interaction['intent']
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        # Get top intents
        top_intents = sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_interactions': len(user_history),
            'top_intents': top_intents,
            'common_topics': list(set([h['intent'] for h in user_history if h['intent'] != 'general'])),
            'last_interaction': user_history[-1]['timestamp'] if user_history else None
        }
    
    def update_user_preferences(self, user_id: str, preferences: Dict):
        """Update user preferences"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        self.user_preferences[user_id].update(preferences)
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences"""
        return self.user_preferences.get(user_id, {})
