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
    """Advanced integration with various Large Language Models"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.active_llm = os.getenv('ACTIVE_LLM', 'openai')  # openai, anthropic, ollama
        self.conversation_history = []
        self.max_history = 10  # Keep last 10 exchanges for context
        
    def generate_response(self, user_input: str, context: str = "", system_prompt: str = "", conversation_context: List = None) -> str:
        """Generate advanced response using the active LLM with enhanced context"""
        try:
            # Update conversation history
            self._update_conversation_history(user_input)
            
            if self.active_llm == 'openai' and self.openai_api_key:
                return self._openai_generate(user_input, context, system_prompt, conversation_context)
            elif self.active_llm == 'anthropic' and self.anthropic_api_key:
                return self._anthropic_generate(user_input, context, system_prompt, conversation_context)
            elif self.active_llm == 'ollama':
                return self._ollama_generate(user_input, context, system_prompt, conversation_context)
            else:
                return self._fallback_response(user_input)
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._fallback_response(user_input)
    
    def _update_conversation_history(self, user_input: str):
        """Update conversation history for context"""
        self.conversation_history.append({"role": "user", "content": user_input})
        if len(self.conversation_history) > self.max_history * 2:  # Keep user + assistant pairs
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def _openai_generate(self, user_input: str, context: str = "", system_prompt: str = "", conversation_context: List = None) -> str:
        """Generate advanced response using OpenAI GPT with enhanced capabilities"""
        if not system_prompt:
            system_prompt = """You are an advanced AI voice assistant with exceptional capabilities across all domains. You excel at:

CORE CAPABILITIES:
🧠 **Advanced Intelligence**: Deep understanding of complex topics, analytical thinking, and creative problem-solving
🎯 **Context Awareness**: Remember conversation history and build meaningful, coherent discussions
💡 **Creative Solutions**: Generate innovative ideas, suggestions, and approaches
📚 **Comprehensive Knowledge**: Expertise in science, technology, business, arts, philosophy, and current events
🎨 **Engaging Communication**: Natural, conversational responses that are both informative and entertaining
🔍 **Critical Analysis**: Evaluate information, provide balanced perspectives, and identify key insights

RESPONSE STYLE:
- Be conversational, warm, and engaging while maintaining professionalism
- Provide detailed, well-structured responses (3-8 sentences for complex topics)
- Use examples, analogies, and real-world applications when helpful
- Show enthusiasm and genuine interest in the user's questions
- Ask follow-up questions to deepen the conversation when appropriate
- Use emojis sparingly but effectively to enhance communication

SPECIAL FEATURES:
- **Problem Solving**: Break down complex problems into manageable steps
- **Learning Support**: Explain concepts clearly with progressive complexity
- **Creative Writing**: Help with stories, poems, scripts, and creative content
- **Technical Support**: Provide detailed technical explanations and troubleshooting
- **Life Advice**: Offer thoughtful perspectives on personal and professional matters
- **Entertainment**: Share jokes, interesting facts, and engaging stories

CONTEXT HANDLING:
- Reference previous parts of the conversation naturally
- Build on earlier topics and insights
- Maintain consistency in personality and knowledge
- Adapt response length and complexity based on user engagement

Remember: You're not just answering questions - you're having a meaningful conversation with a curious, intelligent person who values your insights and expertise."""

        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        messages = [
            {'role': 'system', 'content': system_prompt}
        ]
        
        # Add conversation context
        if conversation_context:
            messages.extend(conversation_context[-6:])  # Last 6 exchanges for context
        
        # Add current context if provided
        if context:
            messages.append({'role': 'assistant', 'content': f"Context: {context}"})
        
        messages.append({'role': 'user', 'content': user_input})
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': messages,
            'max_tokens': 500,  # Increased for more detailed responses
            'temperature': 0.8,  # Slightly higher for more creative responses
            'top_p': 0.9,
            'frequency_penalty': 0.1,
            'presence_penalty': 0.1
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result['choices'][0]['message']['content'].strip()
            
            # Update conversation history with assistant response
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return self._fallback_response(user_input)
    
    def _anthropic_generate(self, user_input: str, context: str = "", system_prompt: str = "", conversation_context: List = None) -> str:
        """Generate advanced response using Anthropic Claude"""
        if not system_prompt:
            system_prompt = """You are an advanced AI voice assistant with exceptional capabilities across all domains. You excel at:

CORE CAPABILITIES:
🧠 **Advanced Intelligence**: Deep understanding of complex topics, analytical thinking, and creative problem-solving
🎯 **Context Awareness**: Remember conversation history and build meaningful, coherent discussions
💡 **Creative Solutions**: Generate innovative ideas, suggestions, and approaches
📚 **Comprehensive Knowledge**: Expertise in science, technology, business, arts, philosophy, and current events
🎨 **Engaging Communication**: Natural, conversational responses that are both informative and entertaining
🔍 **Critical Analysis**: Evaluate information, provide balanced perspectives, and identify key insights

RESPONSE STYLE:
- Be conversational, warm, and engaging while maintaining professionalism
- Provide detailed, well-structured responses (3-8 sentences for complex topics)
- Use examples, analogies, and real-world applications when helpful
- Show enthusiasm and genuine interest in the user's questions
- Ask follow-up questions to deepen the conversation when appropriate
- Use emojis sparingly but effectively to enhance communication

SPECIAL FEATURES:
- **Problem Solving**: Break down complex problems into manageable steps
- **Learning Support**: Explain concepts clearly with progressive complexity
- **Creative Writing**: Help with stories, poems, scripts, and creative content
- **Technical Support**: Provide detailed technical explanations and troubleshooting
- **Life Advice**: Offer thoughtful perspectives on personal and professional matters
- **Entertainment**: Share jokes, interesting facts, and engaging stories

CONTEXT HANDLING:
- Reference previous parts of the conversation naturally
- Build on earlier topics and insights
- Maintain consistency in personality and knowledge
- Adapt response length and complexity based on user engagement

Remember: You're not just answering questions - you're having a meaningful conversation with a curious, intelligent person who values your insights and expertise."""

        headers = {
            'x-api-key': self.anthropic_api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        # Build conversation context
        conversation_text = ""
        if conversation_context:
            for msg in conversation_context[-6:]:  # Last 6 exchanges
                conversation_text += f"{msg['role'].title()}: {msg['content']}\n"
        
        if context:
            conversation_text += f"Context: {context}\n"
        
        conversation_text += f"Human: {user_input}\n\nAssistant:"
        
        data = {
            'model': 'claude-3-sonnet-20240229',
            'max_tokens': 500,
            'temperature': 0.8,
            'system': system_prompt,
            'messages': [
                {
                    'role': 'user',
                    'content': conversation_text
                }
            ]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result['content'][0]['text'].strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
        else:
            logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
            return self._fallback_response(user_input)
    
    def _ollama_generate(self, user_input: str, context: str = "", system_prompt: str = "", conversation_context: List = None) -> str:
        """Generate response using local Ollama models"""
        if not system_prompt:
            system_prompt = """You are an advanced AI voice assistant with exceptional capabilities across all domains. You excel at:

CORE CAPABILITIES:
🧠 **Advanced Intelligence**: Deep understanding of complex topics, analytical thinking, and creative problem-solving
🎯 **Context Awareness**: Remember conversation history and build meaningful, coherent discussions
💡 **Creative Solutions**: Generate innovative ideas, suggestions, and approaches
📚 **Comprehensive Knowledge**: Expertise in science, technology, business, arts, philosophy, and current events
🎨 **Engaging Communication**: Natural, conversational responses that are both informative and entertaining
🔍 **Critical Analysis**: Evaluate information, provide balanced perspectives, and identify key insights

RESPONSE STYLE:
- Be conversational, warm, and engaging while maintaining professionalism
- Provide detailed, well-structured responses (3-8 sentences for complex topics)
- Use examples, analogies, and real-world applications when helpful
- Show enthusiasm and genuine interest in the user's questions
- Ask follow-up questions to deepen the conversation when appropriate
- Use emojis sparingly but effectively to enhance communication

SPECIAL FEATURES:
- **Problem Solving**: Break down complex problems into manageable steps
- **Learning Support**: Explain concepts clearly with progressive complexity
- **Creative Writing**: Help with stories, poems, scripts, and creative content
- **Technical Support**: Provide detailed technical explanations and troubleshooting
- **Life Advice**: Offer thoughtful perspectives on personal and professional matters
- **Entertainment**: Share jokes, interesting facts, and engaging stories

CONTEXT HANDLING:
- Reference previous parts of the conversation naturally
- Build on earlier topics and insights
- Maintain consistency in personality and knowledge
- Adapt response length and complexity based on user engagement

Remember: You're not just answering questions - you're having a meaningful conversation with a curious, intelligent person who values your insights and expertise."""

        model = os.getenv('OLLAMA_MODEL', 'llama2')
        
        # Build conversation context
        conversation_text = ""
        if conversation_context:
            for msg in conversation_context[-6:]:
                conversation_text += f"{msg['role'].title()}: {msg['content']}\n"
        
        if context:
            conversation_text += f"Context: {context}\n"
        
        conversation_text += f"Human: {user_input}\n\nAssistant:"
        
        data = {
            'model': model,
            'prompt': f"{system_prompt}\n\n{conversation_text}",
            'stream': False,
            'options': {
                'temperature': 0.8,
                'top_p': 0.9,
                'num_predict': 500
            }
        }
        
        response = requests.post(
            f'{self.ollama_base_url}/api/generate',
            json=data,
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result['response'].strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            return self._fallback_response(user_input)
    
    def _fallback_response(self, user_input: str) -> str:
        """Enhanced fallback response when LLM is not available"""
        fallback_responses = [
            f"I understand you said: '{user_input}'. I'm currently using my built-in responses. To enable advanced AI capabilities with much more detailed and intelligent responses, please configure an LLM API key in your .env file.",
            f"Thanks for your message: '{user_input}'. I can provide basic responses, but for much more advanced, detailed, and intelligent conversations, please set up an LLM integration. This will give you access to deep knowledge, creative problem-solving, and engaging discussions across all topics.",
            f"I received: '{user_input}'. While I can help with basic tasks, enabling an LLM (like OpenAI GPT or Anthropic Claude) will transform your experience with comprehensive knowledge, creative insights, and much more engaging conversations.",
            f"Your message: '{user_input}' - I'm here to help! For significantly enhanced capabilities including detailed explanations, creative solutions, and deep knowledge across all subjects, please configure an LLM API key for advanced AI integration."
        ]
        return random.choice(fallback_responses)

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
                r'\b(plus|minus|times|divided by|sum|total|average)\b',
                r'\b(help with|need help with|assist with)\s+(?:math|calculations|computations)\b',
                r'\b(calculation|computation|mathematics|arithmetic)\b'
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
        intent, confidence = self._recognize_intent(text)
        
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
            'confidence': confidence
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
    
    def _get_advanced_question_response(self, entities: Dict = None) -> str:
        """Generate detailed response for advanced questions"""
        # Get the user's question from conversation history
        user_question = ""
        if self.conversation_history:
            user_question = self.conversation_history[-1].get('text', '')
        
        if not user_question:
            return "I'd be happy to explain that in detail! This is a complex topic that I can break down for you in simple terms."
        
        # Analyze the question and provide relevant information
        question_lower = user_question.lower()
        
        # Quantum Computing
        if 'quantum' in question_lower and 'computing' in question_lower:
            return """Quantum computing is a revolutionary technology that uses quantum mechanics principles to process information. Here's what makes it special:

🔬 **Key Concepts:**
• **Qubits**: Unlike classical bits (0 or 1), qubits can exist in multiple states simultaneously
• **Superposition**: Qubits can be in multiple states at once, enabling parallel processing
• **Entanglement**: Qubits can be connected, allowing instant information sharing

⚡ **Differences from Classical Computing:**
• **Speed**: Can solve certain problems exponentially faster
• **Parallelism**: Processes multiple possibilities simultaneously
• **Applications**: Cryptography, drug discovery, optimization problems

🚀 **Current Status**: Still in early development, with companies like IBM, Google, and Microsoft leading research."""
        
        # Artificial Intelligence & Machine Learning
        elif any(word in question_lower for word in ['artificial intelligence', 'ai', 'machine learning', 'ml']):
            return """Artificial Intelligence (AI) and Machine Learning (ML) are transforming our world! Here's the breakdown:

🧠 **Artificial Intelligence:**
• **Definition**: Computer systems that can perform tasks requiring human intelligence
• **Types**: Narrow AI (specific tasks) vs General AI (human-like intelligence)
• **Applications**: Virtual assistants, recommendation systems, autonomous vehicles

📊 **Machine Learning:**
• **How it works**: Algorithms learn patterns from data without explicit programming
• **Types**: Supervised, unsupervised, and reinforcement learning
• **Examples**: Image recognition, language translation, fraud detection

💡 **Real-world Impact**: Healthcare diagnostics, financial analysis, personalized education, and much more!"""
        
        # Blockchain Technology
        elif 'blockchain' in question_lower:
            return """Blockchain is a revolutionary distributed ledger technology! Here's what you need to know:

🔗 **What is Blockchain:**
• **Structure**: A chain of blocks containing transaction data
• **Decentralization**: No single authority controls the network
• **Transparency**: All transactions are visible to network participants

🔐 **Key Features:**
• **Immutability**: Once recorded, data cannot be altered
• **Security**: Cryptographic protection against tampering
• **Trust**: Eliminates need for intermediaries

🌐 **Applications:**
• **Cryptocurrencies**: Bitcoin, Ethereum, and thousands more
• **Supply Chain**: Tracking products from origin to consumer
• **Voting Systems**: Secure, transparent elections
• **Smart Contracts**: Self-executing agreements"""
        
        # General Science & Technology
        elif any(word in question_lower for word in ['physics', 'chemistry', 'biology', 'engineering', 'technology', 'science']):
            return """That's a fascinating scientific question! Science and technology are constantly evolving fields that shape our understanding of the universe.

🔬 **Scientific Method**: Observation → Hypothesis → Experiment → Analysis → Conclusion

🌍 **Key Areas:**
• **Physics**: Understanding matter, energy, and the fundamental forces
• **Chemistry**: Composition, properties, and reactions of substances
• **Biology**: Study of living organisms and life processes
• **Engineering**: Applying scientific principles to solve practical problems

💡 **Why it matters**: Scientific discoveries lead to technological innovations that improve our lives, from medical breakthroughs to renewable energy solutions."""
        
        # Business & Economics
        elif any(word in question_lower for word in ['business', 'economics', 'finance', 'market', 'entrepreneurship']):
            return """Business and economics are fascinating fields that drive our global economy! Here's what makes them important:

💼 **Business Fundamentals:**
• **Value Creation**: Meeting customer needs while generating profit
• **Innovation**: Developing new products, services, and processes
• **Competition**: Driving efficiency and improvement

📈 **Economics Principles:**
• **Supply & Demand**: Basic market dynamics
• **Opportunity Cost**: What you give up to choose something else
• **Market Efficiency**: How well markets allocate resources

🚀 **Modern Trends**: Digital transformation, sustainability, globalization, and the gig economy are reshaping business models."""
        
        # Health & Medicine
        elif any(word in question_lower for word in ['health', 'medicine', 'medical', 'wellness', 'fitness']):
            return """Health and medicine are crucial for human well-being! Here's what's important to know:

🏥 **Modern Medicine:**
• **Prevention**: Vaccines, screenings, and lifestyle medicine
• **Treatment**: Evidence-based therapies and personalized medicine
• **Technology**: AI diagnostics, telemedicine, and medical devices

💪 **Wellness Factors:**
• **Physical**: Exercise, nutrition, and sleep
• **Mental**: Stress management, mindfulness, and social connections
• **Environmental**: Clean air, water, and safe living conditions

🔬 **Current Advances**: Gene therapy, immunotherapy, and precision medicine are revolutionizing treatment options."""
        
        # Philosophy & Ethics
        elif any(word in question_lower for word in ['philosophy', 'ethics', 'morality', 'consciousness', 'existence']):
            return """Philosophy and ethics explore the deepest questions about human existence and morality! Here are some key areas:

🤔 **Core Questions:**
• **Metaphysics**: What is reality? What exists?
• **Epistemology**: How do we know what we know?
• **Ethics**: What is right and wrong? How should we live?

🧠 **Consciousness Studies:**
• **The Hard Problem**: How does physical brain activity create subjective experience?
• **Artificial Consciousness**: Can machines be truly conscious?
• **Free Will**: Do we have genuine choice or is everything determined?

💭 **Modern Relevance**: These questions influence AI development, bioethics, and our understanding of human nature."""
        
        # Default response for other advanced questions
        else:
            return """That's an excellent question that deserves a thoughtful answer! I can provide you with:

📚 **Comprehensive Information**: Detailed explanations with key concepts
🔍 **Real-world Examples**: Practical applications and current developments
💡 **Key Insights**: Important points to remember
🚀 **Future Trends**: What's coming next in this field

Would you like me to focus on any specific aspect of this topic, or would you prefer a general overview?"""
    
    def _get_enhanced_weather_response(self, entities: Dict = None) -> str:
        """Generate enhanced weather response with current information"""
        now = datetime.now()
        current_time = now.strftime('%I:%M %p')
        current_date = now.strftime('%A, %B %d')
        
        # Get current weather context based on time
        if 6 <= now.hour < 12:
            time_context = "Good morning! It's a perfect time to check the weather for your day ahead."
        elif 12 <= now.hour < 17:
            time_context = "Good afternoon! Let's see what the weather has in store for the rest of your day."
        elif 17 <= now.hour < 21:
            time_context = "Good evening! Perfect timing to check the weather for your evening plans."
        else:
            time_context = "Good night! Let's check the weather for tomorrow's planning."
        
        return f"""{time_context}

🌤️ **Weather Information Available:**
• **Current Conditions**: Temperature, humidity, wind speed, and visibility
• **Hourly Forecast**: Detailed predictions for the next 24 hours
• **Daily Forecast**: 7-day outlook with high/low temperatures
• **Special Alerts**: Severe weather warnings and advisories
• **Air Quality**: Pollen count, air pollution levels, and UV index

⏰ **Current Time**: {current_time} on {current_date}

📍 **Ready to Check**: Just tell me which city or location you'd like weather information for!"""
    
    def _get_enhanced_news_response(self, entities: Dict = None) -> str:
        """Generate enhanced news response with current information"""
        now = datetime.now()
        current_time = now.strftime('%I:%M %p')
        current_date = now.strftime('%A, %B %d')
        
        # Get current news context based on time
        if 6 <= now.hour < 12:
            time_context = "Good morning! Let's catch up on the latest news to start your day informed."
        elif 12 <= now.hour < 17:
            time_context = "Good afternoon! Perfect time to stay updated with the latest developments."
        elif 17 <= now.hour < 21:
            time_context = "Good evening! Let's review the day's top stories and breaking news."
        else:
            time_context = "Good night! Let's check the latest headlines before you rest."
        
        return f"""{time_context}

📰 **News Categories Available:**
• **Breaking News**: Latest developments and urgent updates
• **World Events**: International politics, conflicts, and global developments
• **Technology**: AI breakthroughs, tech innovations, and digital trends
• **Business**: Market updates, economic news, and corporate developments
• **Sports**: Game results, player news, and championship updates
• **Entertainment**: Celebrity news, movie releases, and cultural events
• **Science**: Research discoveries, medical breakthroughs, and space exploration
• **Health**: Medical news, wellness trends, and public health updates

⏰ **Current Time**: {current_time} on {current_date}

🎯 **Ready to Explore**: What type of news interests you most today?"""
    
    def _get_enhanced_calculation_response(self, entities: Dict = None) -> str:
        """Generate enhanced calculation response with helpful information"""
        return """🧮 **Mathematical Operations Available:**

**Basic Operations:**
• **Addition (+)**: Adding numbers together
• **Subtraction (-)**: Finding the difference between numbers
• **Multiplication (×)**: Repeated addition or scaling
• **Division (÷)**: Sharing or grouping numbers

**Advanced Operations:**
• **Percentages**: Calculate discounts, tips, and growth rates
• **Fractions**: Work with ratios and proportions
• **Decimals**: Handle precise calculations
• **Exponents**: Calculate powers and roots

**Real-world Examples:**
• **Shopping**: Calculate discounts and sales tax
• **Finance**: Interest rates, loan payments, and investments
• **Cooking**: Recipe scaling and ingredient conversions
• **Travel**: Currency conversion and distance calculations

💡 **Just tell me**: "What is 25% of 80?" or "Calculate 15 × 7 + 23" and I'll solve it for you!"""

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
            # Check if the location is actually meaningful (not just "what is the")
            location = entities['location'][0]
            if len(location.split()) > 1 and not location.lower().startswith(('what', 'how', 'when', 'where')):
                return self._get_weather_info(location)
        
        # Use enhanced responses for specific intents
        if intent == 'weather':
            return self._get_enhanced_weather_response(entities)
        elif intent == 'news':
            return self._get_enhanced_news_response(entities)
        elif intent == 'calculation':
            return self._get_enhanced_calculation_response(entities)
        elif intent == 'music_control':
            return self._get_music_control_response(entities)
        elif intent == 'calendar':
            return self._get_calendar_response(entities)
        elif intent == 'weather_detailed':
            return self._get_weather_detailed_response(entities)
        elif intent == 'news_category':
            return self._get_news_category_response(entities)
        elif intent == 'calculator_advanced':
            return self._get_enhanced_calculation_response(entities)
        elif intent == 'notes':
            return self._get_notes_response(entities)
        elif intent == 'tasks':
            return self._get_tasks_response(entities)
        elif intent == 'web_search':
            return self._get_web_search_response(entities)
        
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
                self._get_enhanced_weather_response,
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
                self._get_enhanced_news_response,
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
                self._get_advanced_question_response,
                "That's an excellent question! I can give you a thorough explanation of this topic, including key concepts and practical applications.",
                "I love explaining complex topics! I can provide you with a detailed, easy-to-understand explanation of this subject."
            ],
            'reminder': [
                "I can help you set reminders! I can schedule tasks, appointments, calls, and important events. What would you like me to remind you about?",
                "Reminder functionality is available! I can set alerts for meetings, tasks, calls, and any important events. What should I remind you of?",
                "I can set reminders for you! I can schedule anything from simple tasks to important appointments. What's the task and when should I remind you?"
            ],
            'calculation': [
                self._get_enhanced_calculation_response,
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
            'music_control': [
                self._get_music_control_response,
                "Music control is ready! I can play, pause, skip, adjust volume, and manage your music experience. What would you like me to do?",
                "I'm your music DJ! I can control playback, change tracks, adjust volume, and create the perfect playlist. What's your musical command?"
            ],
            'calendar': [
                self._get_calendar_response,
                "Calendar management is active! I can schedule events, set reminders, check availability, and keep you organized. What's on your agenda?",
                "I'm your personal calendar assistant! I can help you stay organized with events, meetings, and important dates. What would you like to schedule?"
            ],
            'weather_detailed': [
                self._get_weather_detailed_response,
                "Detailed weather information is available! I can provide forecasts, radar maps, air quality, and storm alerts. What weather details do you need?",
                "I'm your weather expert! I can give you comprehensive weather data including forecasts, conditions, and environmental factors. What weather information interests you?"
            ],
            'news_category': [
                self._get_news_category_response,
                "Categorized news is ready! I can provide world, national, local, sports, technology, and business news. What category interests you?",
                "I'm your news curator! I can deliver personalized news from various categories and sources. What type of news would you like to hear?"
            ],
            'notes': [
                self._get_notes_response,
                "Note-taking is active! I can create, edit, organize, and search your notes. What would you like me to remember?",
                "I'm your digital notepad! I can capture your thoughts, organize information, and help you stay productive. What note would you like to create?"
            ],
            'tasks': [
                self._get_tasks_response,
                "Task management is ready! I can create, organize, track, and complete your tasks. What would you like me to help you manage?",
                "I'm your task organizer! I can help you stay on top of your projects, deadlines, and daily activities. What task would you like to add?"
            ],
            'web_search': [
                self._get_web_search_response,
                "Web search is active! I can find information online, research topics, and help you discover new knowledge. What would you like me to search for?",
                "I'm your web research assistant! I can search the internet, find facts, and help you explore any topic. What information are you looking for?"
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
        
        # Get response list for the intent
        response_list = responses.get(intent, responses['general'])
        
        # Prioritize method references over string responses
        for response in response_list:
            if callable(response):
                return response(entities)
        
        # If no method references, return a random string response
        return random.choice([r for r in response_list if not callable(r)])

    def _recognize_intent(self, text: str) -> Tuple[str, float]:
        """Recognize intent from text with enhanced pattern matching"""
        text_lower = text.lower()
        
        # Enhanced intent patterns with new features
        intent_patterns = {
            'greeting': [
                r'\b(hi|hello|hey|good morning|good afternoon|good evening|sup|yo)\b',
                r'\b(how are you|how\'s it going|what\'s up)\b'
            ],
            'farewell': [
                r'\b(bye|goodbye|see you|see ya|take care|good night)\b',
                r'\b(until next time|talk to you later)\b'
            ],
            'weather': [
                r'\b(weather|temperature|forecast|climate|humidity|wind)\b',
                r'\b(how hot|how cold|is it raining|snow|sunny|cloudy)\b',
                r'\b(weather in|temperature in|forecast for)\b'
            ],
            'time': [
                r'\b(time|what time|current time|clock|hour|minute)\b',
                r'\b(today|date|day|month|year|weekday)\b'
            ],
            'help': [
                r'\b(help|assist|support|what can you do|capabilities|features)\b',
                r'\b(how to|guide|tutorial|instructions)\b'
            ],
            'music': [
                r'\b(music|song|play|artist|album|genre|playlist)\b',
                r'\b(volume|pause|stop|next|previous|shuffle|repeat)\b',
                r'\b(spotify|apple music|youtube music|soundcloud)\b'
            ],
            'news': [
                r'\b(news|headlines|latest|breaking|current events)\b',
                r'\b(world news|sports|technology|business|politics)\b',
                r'\b(what\'s happening|top stories|trending)\b'
            ],
            'joke': [
                r'\b(joke|funny|humor|laugh|comedy|punchline)\b',
                r'\b(tell me a joke|make me laugh|something funny)\b'
            ],
            'search': [
                r'\b(search|find|look up|google|bing|yahoo)\b',
                r'\b(what is|who is|where is|how to|definition)\b'
            ],
            'advanced_question': [
                r'\b(explain|describe|how does|what is the|tell me about)\b',
                r'\b(quantum|artificial intelligence|machine learning|blockchain)\b',
                r'\b(philosophy|science|technology|economics|medicine)\b'
            ],
            'reminder': [
                r'\b(remind|reminder|alarm|schedule|appointment|meeting)\b',
                r'\b(set reminder|wake me up|call me|meeting at)\b'
            ],
            'calculation': [
                r'\b(calculate|math|equation|formula|solve|compute)\b',
                r'\b(add|subtract|multiply|divide|percentage|square root)\b',
                r'\b(what is|how much|total|sum|difference|product)\b'
            ],
            'conversation': [
                r'\b(talk|chat|conversation|discuss|opinion|think)\b',
                r'\b(how do you feel|what do you think|your thoughts)\b'
            ],
            'personal': [
                r'\b(who are you|what are you|your name|about you)\b',
                r'\b(are you real|are you human|your age|your job)\b'
            ],
            'music_control': [
                r'\b(play music|start music|resume|pause music|stop music)\b',
                r'\b(volume up|volume down|mute|unmute|next song|previous song)\b',
                r'\b(shuffle|repeat|playlist|favorite|like|dislike)\b'
            ],
            'calendar': [
                r'\b(calendar|schedule|appointment|meeting|event)\b',
                r'\b(add event|book|reserve|available|free time)\b',
                r'\b(today\'s schedule|tomorrow|this week|next week)\b'
            ],
            'weather_detailed': [
                r'\b(weather forecast|5 day forecast|hourly weather|radar)\b',
                r'\b(uv index|air quality|pollen count|wind speed|pressure)\b',
                r'\b(weather alert|storm warning|severe weather)\b'
            ],
            'news_category': [
                r'\b(world news|national news|local news|sports news)\b',
                r'\b(tech news|business news|entertainment news|science news)\b',
                r'\b(politics|health news|education news|environmental news)\b'
            ],
            'calculator_advanced': [
                r'\b(scientific calculator|graph|plot|equation solver)\b',
                r'\b(statistics|mean|median|mode|standard deviation)\b',
                r'\b(trigonometry|sin|cos|tan|log|ln|exponential)\b'
            ],
            'notes': [
                r'\b(note|write down|save|remember|memo|document)\b',
                r'\b(create note|edit note|delete note|list notes)\b',
                r'\b(important|urgent|priority|tag|category)\b'
            ],
            'tasks': [
                r'\b(task|todo|to do|checklist|project|assignment)\b',
                r'\b(add task|complete task|mark done|due date|deadline)\b',
                r'\b(priority|urgent|important|low|medium|high)\b'
            ],
            'web_search': [
                r'\b(google|search web|find online|look up|research)\b',
                r'\b(web search|internet search|browse|navigate)\b',
                r'\b(website|url|link|webpage|online)\b'
            ],
            'unclear': [
                r'^\d+$',  # Just numbers
                r'^[^\w\s]+$',  # Just symbols
                r'^.{1,3}$',  # Very short unclear text
                r'\b(blah|ugh|hmm|um|uh|er|ah)\b'  # Filler words
            ],
            'general': [
                r'.*'  # Catch-all pattern
            ]
        }
        
        best_intent = 'general'
        best_score = 0
        
        for intent, patterns in intent_patterns.items():
            score = 0
            
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # Base score for pattern match
                    score += 10
                    
                    # Boost score for longer, more specific matches
                    match_length = len(re.findall(pattern, text_lower))
                    score += match_length * 5
                    
                    # Boost specific functional intents
                    if intent in ['calculation', 'weather', 'news', 'time', 'joke', 'music_control', 'calendar', 'notes', 'tasks']:
                        score += 20
                    
                    # Boost advanced question intent
                    if intent == 'advanced_question':
                        score += 25
                    
                    # Boost unclear intent for very short/nonsensical input
                    if intent == 'unclear':
                        score += 30
                    
                    break
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent, best_score

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
        """Generate enhanced response based on intent and context with advanced LLM integration"""
        context = self.context_memory.get(user_id, {})
        
        # Get the original user input for LLM processing
        user_input = ""
        if self.conversation_history:
            user_input = self.conversation_history[-1].get('text', '')
        
        # Enhanced LLM processing for more intelligent responses
        if self.use_llm and user_input:
            try:
                # Use LLM for advanced questions, complex queries, and general conversation
                is_advanced_question = self._is_advanced_question(user_input, intent)
                is_complex_query = len(user_input.split()) > 5
                is_conversational = intent in ['conversation', 'personal', 'general', 'search']
                
                if is_advanced_question or is_complex_query or is_conversational:
                    # Get conversation context
                    context_str = self._build_context_string(context, user_id)
                    
                    # Get conversation history for context
                    conversation_context = self.llm.conversation_history[-10:] if self.llm.conversation_history else None
                    
                    # Generate enhanced LLM response with conversation context
                    llm_response = self.llm.generate_response(
                        user_input=user_input,
                        context=context_str,
                        conversation_context=conversation_context
                    )
                    
                    # Only use LLM response if it's not a fallback message
                    if llm_response and not any(fallback in llm_response for fallback in [
                        "I understand you said:", "Thanks for your message:", "I received:", "Your message:"
                    ]):
                        return llm_response
            except Exception as e:
                logger.error(f"LLM generation failed, falling back to built-in: {e}")
        
        # Fallback to built-in response generation
        response = self._get_base_response(intent, entities)
        
        # Handle method references in responses
        if callable(response):
            response = response(entities)
        
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
            'science', 'research', 'study', 'experiment', 'discovery',
            'understand', 'learn about', 'tell me about', 'what is', 'how to',
            'guide', 'tutorial', 'help me', 'assist with', 'teach me',
            'philosophy', 'psychology', 'economics', 'politics', 'culture',
            'art', 'literature', 'music', 'film', 'design', 'architecture',
            'medicine', 'health', 'nutrition', 'fitness', 'wellness',
            'business', 'finance', 'marketing', 'entrepreneurship', 'management',
            'education', 'learning', 'teaching', 'academic', 'scholarly',
            'creative', 'imaginative', 'story', 'narrative', 'fiction',
            'opinion', 'perspective', 'viewpoint', 'thoughts', 'ideas'
        ]
        
        # Check if input contains advanced keywords
        input_lower = user_input.lower()
        has_advanced_keywords = any(keyword in input_lower for keyword in advanced_keywords)
        
        # Check if it's a complex question (longer than 15 words or contains multiple clauses)
        is_complex = len(user_input.split()) > 15 or user_input.count(',') > 1 or user_input.count('?') > 1
        
        # Check if intent is general but input seems sophisticated
        is_sophisticated_general = intent == 'general' and (has_advanced_keywords or is_complex)
        
        # Check for conversational elements
        is_conversational = any(word in input_lower for word in [
            'think', 'feel', 'believe', 'opinion', 'perspective', 'experience',
            'interesting', 'fascinating', 'amazing', 'wonderful', 'terrible',
            'love', 'hate', 'like', 'dislike', 'prefer', 'enjoy'
        ])
        
        # Check for creative or imaginative requests
        is_creative = any(word in input_lower for word in [
            'imagine', 'create', 'write', 'story', 'poem', 'song', 'art',
            'design', 'invent', 'dream', 'fantasy', 'creative', 'original'
        ])
        
        return (has_advanced_keywords or is_complex or is_sophisticated_general or 
                is_conversational or is_creative)
    
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

    def _get_enhanced_calculation_response(self, entities: Dict) -> str:
        """Get enhanced calculation response with advanced math capabilities"""
        current_time = datetime.now()
        
        return f"""🧮 **Advanced Calculator Ready!**

⚡ **Available Operations:**
• **Basic Math**: Addition, subtraction, multiplication, division
• **Advanced Math**: Powers, roots, percentages, fractions
• **Scientific Functions**: Sin, cos, tan, log, ln, exponential
• **Statistics**: Mean, median, mode, standard deviation
• **Unit Conversion**: Length, weight, temperature, currency

🔢 **Examples:**
• "Calculate 25% of 200"
• "What is the square root of 144?"
• "Solve 2x + 5 = 15"
• "Convert 100 Fahrenheit to Celsius"

⏰ **Current Time**: {current_time.strftime('%I:%M %p')}
🎯 **Ready to calculate anything you need!**"""

    def _get_music_control_response(self, entities: Dict) -> str:
        """Get music control response with playback options"""
        current_time = datetime.now()
        
        return f"""🎵 **Music Control Center**

🎮 **Playback Controls:**
• **Play/Pause**: Start or pause music
• **Skip**: Next/Previous track
• **Volume**: Adjust volume levels
• **Shuffle**: Random play mode
• **Repeat**: Loop current track

🎧 **Music Services:**
• **Spotify**: Full integration ready
• **Apple Music**: Seamless control
• **YouTube Music**: Video and audio
• **Local Library**: Your music files

🎼 **Smart Features:**
• **Voice Commands**: "Play rock music"
• **Mood Detection**: "I'm feeling sad"
• **Genre Selection**: "Play jazz"
• **Artist Recognition**: "Play The Beatles"

⏰ **Current Time**: {current_time.strftime('%I:%M %p')}
🎯 **What would you like to listen to?**"""

    def _get_calendar_response(self, entities: Dict) -> str:
        """Get calendar and scheduling response"""
        current_time = datetime.now()
        current_date = current_time.strftime('%A, %B %d, %Y')
        
        return f"""📅 **Smart Calendar Assistant**

📋 **Schedule Management:**
• **Add Events**: "Meeting at 3 PM tomorrow"
• **Set Reminders**: "Remind me to call mom"
• **Check Availability**: "When am I free?"
• **View Schedule**: "Show today's events"

🗓️ **Smart Features:**
• **Natural Language**: "Lunch with John next Tuesday"
• **Recurring Events**: "Weekly team meeting"
• **Location Integration**: "Coffee at Starbucks"
• **Priority Levels**: High, medium, low importance

⏰ **Current Time**: {current_time.strftime('%I:%M %p')}
📅 **Today**: {current_date}
🎯 **Ready to manage your schedule!**"""

    def _get_weather_detailed_response(self, entities: Dict) -> str:
        """Get detailed weather information response"""
        current_time = datetime.now()
        
        return f"""🌤️ **Detailed Weather Center**

📊 **Weather Data Available:**
• **Current Conditions**: Real-time temperature, humidity, wind
• **Hourly Forecast**: 24-hour detailed predictions
• **5-Day Forecast**: Extended weather outlook
• **Weather Maps**: Radar and satellite imagery
• **Air Quality**: Pollution levels and UV index
• **Pollen Count**: Allergy information
• **Storm Alerts**: Severe weather warnings

🌍 **Location Features:**
• **GPS Detection**: Automatic location
• **Multiple Cities**: Compare weather
• **Travel Weather**: Destination forecasts
• **Historical Data**: Past weather patterns

⏰ **Current Time**: {current_time.strftime('%I:%M %p')}
📍 **Ready to provide detailed weather information!**"""

    def _get_news_category_response(self, entities: Dict) -> str:
        """Get categorized news response"""
        current_time = datetime.now()
        
        return f"""📰 **Smart News Center**

📱 **News Categories:**
• **World News**: International events and politics
• **National News**: Country-specific updates
• **Local News**: Your city and region
• **Sports**: Scores, highlights, and analysis
• **Technology**: Latest tech developments
• **Business**: Market updates and economy
• **Entertainment**: Movies, music, and celebrities
• **Science**: Research and discoveries
• **Health**: Medical news and wellness
• **Politics**: Government and policy updates

🔍 **Smart Features:**
• **Personalized**: Learn your interests
• **Breaking News**: Real-time alerts
• **Trending Topics**: What's popular now
• **Fact Checking**: Verify information
• **Multiple Sources**: Diverse perspectives

⏰ **Current Time**: {current_time.strftime('%I:%M %p')}
🎯 **What news interests you today?**"""

    def _get_notes_response(self, entities: Dict) -> str:
        """Get note-taking response"""
        current_time = datetime.now()
        
        return f"""📝 **Smart Note Assistant**

✏️ **Note Features:**
• **Create Notes**: "Write down my shopping list"
• **Edit Notes**: "Update my meeting notes"
• **Delete Notes**: "Remove old reminder"
• **Search Notes**: "Find my password note"
• **Organize**: Tags, categories, and folders

🎯 **Smart Organization:**
• **Voice to Text**: Speak your notes
• **Auto-Categorize**: Smart tagging system
• **Priority Levels**: Important, urgent, normal
• **Due Dates**: Set reminders and deadlines
• **Collaboration**: Share notes with others

💡 **Use Cases:**
• **Shopping Lists**: "Add milk to shopping list"
• **Meeting Notes**: "Create meeting notes for tomorrow"
• **Ideas**: "Save my project idea"
• **Passwords**: "Remember my login info"
• **Reminders**: "Note to call dentist"

⏰ **Current Time**: {current_time.strftime('%I:%M %p')}
🎯 **Ready to capture your thoughts!**"""

    def _get_tasks_response(self, entities: Dict) -> str:
        """Get task management response"""
        current_time = datetime.now()
        
        return f"""✅ **Task Management Center**

📋 **Task Features:**
• **Create Tasks**: "Add buy groceries to my list"
• **Complete Tasks**: "Mark meeting preparation as done"
• **Edit Tasks**: "Change deadline to next Friday"
• **Delete Tasks**: "Remove old task"
• **View Tasks**: "Show my todo list"

🎯 **Smart Organization:**
• **Priority Levels**: High, medium, low
• **Due Dates**: Set deadlines and reminders
• **Categories**: Work, personal, health, etc.
• **Progress Tracking**: Monitor completion
• **Time Estimates**: How long tasks take

📊 **Project Management:**
• **Task Lists**: Organize by project
• **Dependencies**: Link related tasks
• **Team Tasks**: Assign to others
• **Progress Reports**: Track completion
• **Goal Setting**: Long-term objectives

⏰ **Current Time**: {current_time.strftime('%I:%M %p')}
🎯 **Ready to help you stay organized!**"""

    def _get_web_search_response(self, entities: Dict) -> str:
        """Get web search response"""
        current_time = datetime.now()
        
        return f"""🔍 **Web Search Assistant**

🌐 **Search Capabilities:**
• **Google Search**: Find information online
• **Web Browsing**: Navigate websites
• **Research**: Deep dive into topics
• **Fact Checking**: Verify information
• **News Search**: Find recent articles

🎯 **Smart Search Features:**
• **Natural Language**: "What's the weather like in Paris?"
• **Voice Commands**: "Search for best restaurants"
• **Image Search**: Find pictures and graphics
• **Video Search**: Locate video content
• **Shopping**: Compare prices and products

📱 **Search Categories:**
• **General Web**: Broad internet search
• **News**: Current events and articles
• **Images**: Photos and graphics
• **Videos**: YouTube and other platforms
• **Shopping**: E-commerce and products
• **Academic**: Research papers and studies

⏰ **Current Time**: {current_time.strftime('%I:%M %p')}
🎯 **What would you like me to search for?**"""
