from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import speech_recognition as sr
import pyttsx3
import json
import os
import threading
import queue
import time
from datetime import datetime
import logging
from dotenv import load_dotenv
from config import Config
from nlp_engine import NLPEngine

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Validate configuration
config_issues = Config.validate_config()
for issue in config_issues:
    logger.warning(issue)

class VoiceChatbot:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        
        # Initialize NLP engine
        self.nlp_engine = NLPEngine()
        
        # Configure text-to-speech engine
        tts_config = Config.get_tts_config()
        self.engine.setProperty('rate', tts_config['rate'])
        self.engine.setProperty('volume', tts_config['volume'])
        
        # Get available voices and set a good one
        voices = self.engine.getProperty('voices')
        if voices:
            if tts_config['voice_id']:
                self.engine.setProperty('voice', tts_config['voice_id'])
            else:
                # Try to find a better voice for clarity
                preferred_voices = [
                    'com.apple.speech.synthesis.voice.alex',
                    'com.apple.speech.synthesis.voice.samantha',
                    'com.apple.speech.synthesis.voice.daniel',
                    'com.apple.speech.synthesis.voice.karen',
                    'com.apple.speech.synthesis.voice.tom'
                ]
                voice_found = False
                
                for preferred_voice in preferred_voices:
                    for voice in voices:
                        if preferred_voice in voice.id.lower():
                            self.engine.setProperty('voice', voice.id)
                            voice_found = True
                            logger.info(f"Using voice: {voice.name} ({voice.id})")
                            break
                    if voice_found:
                        break
                
                if not voice_found:
                    # Use a clear English voice if available
                    for voice in voices:
                        if 'en-us' in voice.id.lower() or 'en_gb' in voice.id.lower():
                            self.engine.setProperty('voice', voice.id)
                            logger.info(f"Using English voice: {voice.name} ({voice.id})")
                            break
                    else:
                        # Use the first available voice
                        self.engine.setProperty('voice', voices[0].id)
                        logger.info(f"Using default voice: {voices[0].name} ({voices[0].id})")
                
                # Set rate and volume
                self.engine.setProperty('rate', Config.TTS_RATE)
                self.engine.setProperty('volume', Config.TTS_VOLUME)
                logger.info(f"TTS configured - Rate: {Config.TTS_RATE}, Volume: {Config.TTS_VOLUME}")
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Calibrate microphone
        speech_config = Config.get_speech_config()
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=speech_config['ambient_noise_duration'])
    
    def listen_for_speech(self):
        """Listen for speech input and convert to text"""
        try:
            speech_config = Config.get_speech_config()
            with self.microphone as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=speech_config['timeout'], 
                    phrase_time_limit=speech_config['phrase_time_limit']
                )
                
            logger.info("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            logger.info("No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            logger.info("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return None
    
    def speak(self, text):
        """Convert text to speech with improved clarity"""
        try:
            logger.info(f"Speaking: {text}")
            
            # Clean up text for better pronunciation
            cleaned_text = text.replace(':', ' ').replace('-', ' ').replace('(', ' ').replace(')', ' ')
            
            # Simple approach - just speak the text clearly
            self.engine.say(cleaned_text)
            self.engine.runAndWait()
            logger.info("Speech completed successfully")
                
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            # Try a fallback approach
            try:
                logger.info("Trying fallback TTS...")
                import subprocess
                subprocess.run(['say', cleaned_text], check=True)
                logger.info("Fallback TTS completed")
            except Exception as fallback_error:
                logger.error(f"Fallback TTS also failed: {fallback_error}")
    
    def process_nlp(self, user_input, user_id='default'):
        """Process natural language input and generate response using advanced NLP"""
        # Process with NLP engine
        nlp_result = self.nlp_engine.process_input(user_input, user_id)
        
        # Add to conversation history
        self.conversation_history.append({
            'user': user_input,
            'intent': nlp_result['intent'],
            'entities': nlp_result['entities'],
            'sentiment': nlp_result['sentiment'],
            'confidence': nlp_result['confidence'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Add response to history
        self.conversation_history.append({
            'bot': nlp_result['response'],
            'timestamp': datetime.now().isoformat()
        })
        
        return nlp_result['response']
    

    
    def start_listening(self):
        """Start continuous listening for speech"""
        self.is_listening = True
        while self.is_listening:
            text = self.listen_for_speech()
            if text:
                response = self.process_nlp(text)
                self.speak(response)
            time.sleep(0.1)
    
    def stop_listening(self):
        """Stop listening for speech"""
        self.is_listening = False

# Initialize chatbot
chatbot = VoiceChatbot()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/start-listening', methods=['POST'])
def start_listening():
    """Start listening for speech input"""
    try:
        if not chatbot.is_listening:
            thread = threading.Thread(target=chatbot.start_listening)
            thread.daemon = True
            thread.start()
            return jsonify({'status': 'success', 'message': 'Started listening'})
        else:
            return jsonify({'status': 'error', 'message': 'Already listening'})
    except Exception as e:
        logger.error(f"Error starting listening: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop-listening', methods=['POST'])
def stop_listening():
    """Stop listening for speech input"""
    try:
        chatbot.stop_listening()
        return jsonify({'status': 'success', 'message': 'Stopped listening'})
    except Exception as e:
        logger.error(f"Error stopping listening: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/process-text', methods=['POST'])
def process_text():
    """Process text input and return response"""
    try:
        data = request.get_json()
        user_input = data.get('text', '').strip()
        
        if not user_input:
            return jsonify({'status': 'error', 'message': 'No text provided'})
        
        response = chatbot.process_nlp(user_input)
        return jsonify({
            'status': 'success',
            'response': response,
            'conversation_history': chatbot.conversation_history[-10:]  # Last 10 exchanges
        })
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/speak', methods=['POST'])
def speak_text():
    """Convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'status': 'error', 'message': 'No text provided'})
        
        chatbot.speak(text)
        return jsonify({'status': 'success', 'message': 'Text spoken'})
    except Exception as e:
        logger.error(f"Error speaking text: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/conversation-history', methods=['GET'])
def get_conversation_history():
    """Get conversation history"""
    try:
        return jsonify({
            'status': 'success',
            'history': chatbot.conversation_history
        })
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get chatbot status"""
    try:
        return jsonify({
            'status': 'success',
            'is_listening': chatbot.is_listening,
            'conversation_count': len(chatbot.conversation_history)
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/conversation-summary', methods=['GET'])
def get_conversation_summary():
    """Get conversation summary and analytics"""
    try:
        user_id = request.args.get('user_id', 'default')
        summary = chatbot.nlp_engine.get_conversation_summary(user_id)
        return jsonify({
            'status': 'success',
            'summary': summary
        })
    except Exception as e:
        logger.error(f"Error getting conversation summary: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/user-preferences', methods=['GET', 'POST'])
def manage_user_preferences():
    """Get or update user preferences"""
    try:
        user_id = request.args.get('user_id', 'default')
        
        if request.method == 'POST':
            data = request.get_json()
            chatbot.nlp_engine.update_user_preferences(user_id, data)
            return jsonify({'status': 'success', 'message': 'Preferences updated'})
        else:
            preferences = chatbot.nlp_engine.get_user_preferences(user_id)
            return jsonify({
                'status': 'success',
                'preferences': preferences
            })
    except Exception as e:
        logger.error(f"Error managing user preferences: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/nlp-analysis', methods=['POST'])
def analyze_text():
    """Analyze text with NLP without generating response"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        user_id = data.get('user_id', 'default')
        
        if not text:
            return jsonify({'status': 'error', 'message': 'No text provided'})
        
        nlp_result = chatbot.nlp_engine.process_input(text, user_id)
        return jsonify({
            'status': 'success',
            'analysis': {
                'intent': nlp_result['intent'],
                'entities': nlp_result['entities'],
                'sentiment': nlp_result['sentiment'],
                'confidence': nlp_result['confidence']
            }
        })
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/features', methods=['GET'])
def get_features():
    """Get available chatbot features"""
    features = {
        'core_features': {
            'voice_recognition': 'Speech-to-text conversion',
            'text_to_speech': 'Text-to-speech with 150 WPM',
            'intent_recognition': 'Smart intent classification',
            'llm_integration': 'OpenAI GPT-3.5-turbo support'
        },
        'new_features': {
            'music_control': 'Play, pause, skip, volume control',
            'calendar': 'Schedule management and reminders',
            'weather_detailed': 'Comprehensive weather information',
            'news_category': 'Categorized news delivery',
            'calculator_advanced': 'Scientific and statistical calculations',
            'notes': 'Voice note-taking and organization',
            'tasks': 'Task management and project tracking',
            'web_search': 'Internet search and research'
        },
        'productivity': {
            'reminders': 'Smart reminder system',
            'search': 'Information lookup and search',
            'conversation': 'Natural language processing',
            'context_memory': 'Conversation history tracking'
        }
    }
    return jsonify(features)

@app.route('/api/test-feature/<feature>', methods=['POST'])
def test_feature(feature):
    """Test specific chatbot features"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Process the text through NLP engine
        result = chatbot.nlp_engine.process_input(text, 'test_user')
        
        return jsonify({
            'feature': feature,
            'input': text,
            'intent': result.get('intent'),
            'confidence': result.get('confidence'),
            'response': result.get('response'),
            'entities': result.get('entities')
        })
        
    except Exception as e:
        logger.error(f"Error testing feature {feature}: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(
        debug=Config.DEBUG, 
        host=Config.HOST, 
        port=Config.PORT
    )
