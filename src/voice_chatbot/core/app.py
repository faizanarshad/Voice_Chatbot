from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import speech_recognition as sr
import json
import os
import threading
import queue
import time
import tempfile
from datetime import datetime
import logging
from dotenv import load_dotenv
from .config import Config
from ..services.nlp_engine import NLPEngine

# Import additional TTS libraries
try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
    pygame.mixer.init()
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    PYTTSX3_AVAILABLE = False

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
        
        # Initialize TTS engines with multiple fallback options
        self.tts_methods = []
        
        # Method 1: Try pyttsx3 with proper macOS support
        if PYTTSX3_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.tts_methods.append('pyttsx3')
                logger.info("✅ pyttsx3 TTS engine initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ pyttsx3 TTS engine initialization failed: {e}")
                self.engine = None
        
        # Method 2: macOS system 'say' command (always available on macOS - most reliable)
        self.tts_methods.append('say')
        logger.info("✅ macOS system 'say' command available")
        
        # Method 3: Google Text-to-Speech (fallback option)
        if GTTS_AVAILABLE:
            self.tts_methods.append('gtts')
            logger.info("✅ Google TTS (gTTS) available")
        
        # Set primary TTS method
        self.primary_tts = self.tts_methods[0] if self.tts_methods else 'say'
        logger.info(f"🎯 Primary TTS method: {self.primary_tts}")
        
        self.audio_queue = queue.Queue()
        self.is_listening = False
        
        # Initialize NLP engine
        self.nlp_engine = NLPEngine()
        
        # Configure text-to-speech engine (only for pyttsx3)
        if 'pyttsx3' in self.tts_methods and self.engine:
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
            
            # Create a new microphone instance to avoid context manager conflicts
            microphone = sr.Microphone()
            
            try:
                with microphone as source:
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
                
            except Exception as mic_error:
                logger.error(f"Microphone error: {mic_error}")
                return None
                
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
    
    def listen_for_speech_from_file(self, audio_file):
        """Listen for speech from uploaded audio file and convert to text"""
        try:
            import io
            
            logger.info(f"Processing audio file: {audio_file.filename}")
            
            # Read uploaded audio bytes
            audio_bytes = audio_file.read()
            if not audio_bytes:
                logger.error("Uploaded audio file is empty")
                return None
            
            # Determine format from filename or content
            filename = (audio_file.filename or '').lower()
            if filename.endswith('.webm') or filename.endswith('.opus'):
                audio_format = 'webm'
            elif filename.endswith('.wav'):
                audio_format = 'wav'
            elif filename.endswith('.mp4') or filename.endswith('.m4a'):
                audio_format = 'mp4'
            else:
                audio_format = 'webm'  # Browser typically sends WebM
            
            try:
                from pydub import AudioSegment
                # Load audio from bytes
                audio_segment = AudioSegment.from_file(
                    io.BytesIO(audio_bytes),
                    format=audio_format
                )
                # Export to WAV for SpeechRecognition (16kHz mono)
                audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
                wav_buffer = io.BytesIO()
                audio_segment.export(wav_buffer, format='wav')
                wav_buffer.seek(0)
            except Exception as conv_err:
                logger.error(f"PyDub conversion failed: {conv_err}. Install ffmpeg: brew install ffmpeg")
                return None
            
            # Use SpeechRecognition with the WAV file
            # Chunk long audio (Google API ~60s limit) for full conversation capture
            transcripts = []
            with sr.AudioFile(wav_buffer) as source:
                while True:
                    try:
                        audio_data = self.recognizer.record(source, duration=55)
                        if len(audio_data.get_raw_data()) < 1000:
                            break  # No significant audio left
                        chunk_text = self.recognizer.recognize_google(audio_data)
                        if chunk_text:
                            transcripts.append(chunk_text)
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError as e:
                        logger.error(f"Speech API error: {e}")
                        break
                    except Exception:
                        break
            
            if not transcripts:
                return None
            text = ' '.join(transcripts)
            logger.info(f"Recognized from file: {text[:100]}...")
            return text.lower()
            
        except sr.UnknownValueError:
            logger.warning("Could not understand audio in file")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            return None
    
    def speak(self, text):
        """Convert text to speech using multiple TTS methods with fallbacks"""
        logger.info(f"🗣️ Speaking: {text[:100]}...")
        logger.info(f"🎯 Available TTS methods: {self.tts_methods}")
        logger.info(f"🎯 Primary TTS method: {self.primary_tts}")
        
        # Clean up text for better pronunciation
        cleaned_text = text.replace(':', ' ').replace('-', ' ').replace('(', ' ').replace(')', ' ')
        
        # Try each TTS method in order of preference
        for method in self.tts_methods:
            try:
                logger.info(f"🔄 Attempting TTS method: {method}")
                
                if method == 'pyttsx3' and self.engine:
                    logger.info("🎯 Using pyttsx3 TTS...")
                    self.engine.say(cleaned_text)
                    self.engine.runAndWait()
                    logger.info("✅ pyttsx3 TTS completed successfully")
                    return
                    
                elif method == 'gtts' and GTTS_AVAILABLE:
                    logger.info("🌐 Using Google TTS (gTTS)...")
                    self._speak_with_gtts(cleaned_text)
                    logger.info("✅ Google TTS completed successfully")
                    return
                    
                elif method == 'say':
                    logger.info("🍎 Using macOS system 'say' command...")
                    import subprocess
                    
                    # Speak in chunks for long text (full answer, no truncation)
                    max_chunk = 1500  # Characters per chunk; say handles this well
                    chunks = [cleaned_text[i:i + max_chunk] for i in range(0, len(cleaned_text), max_chunk)]
                    for chunk in chunks:
                        if chunk.strip():
                            subprocess.run(['say', chunk], check=True, timeout=90, capture_output=True, text=True)
                    logger.info("✅ macOS 'say' command completed successfully")
                    return
                    
            except Exception as e:
                logger.warning(f"⚠️ TTS method '{method}' failed: {e}")
                continue
        
        logger.error("❌ All TTS methods failed!")
    
    def _speak_with_gtts(self, text):
        """Use Google Text-to-Speech with pygame for audio playback"""
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                temp_audio_file = tmp_file.name
            
            # Generate speech with gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_audio_file)
            
            # Play audio with pygame
            pygame.mixer.music.load(temp_audio_file)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Clean up temporary file
            os.unlink(temp_audio_file)
            
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            raise
    
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

# Routes moved to src/voice_chatbot/api/routes.py

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
    """Get enhanced chatbot status with LLM information"""
    try:
        # Get LLM configuration
        llm_enabled = chatbot.nlp_engine.use_llm
        active_llm = chatbot.nlp_engine.llm.active_llm if llm_enabled else 'none'
        
        # Check LLM API keys
        llm_status = 'configured'
        if llm_enabled:
            if active_llm == 'openai' and not chatbot.nlp_engine.llm.openai_api_key:
                llm_status = 'missing_api_key'
            elif active_llm == 'anthropic' and not chatbot.nlp_engine.llm.anthropic_api_key:
                llm_status = 'missing_api_key'
            elif active_llm == 'ollama':
                llm_status = 'local_model'
        
        return jsonify({
            'status': 'success',
            'is_listening': chatbot.is_listening,
            'conversation_count': len(chatbot.conversation_history),
            'llm_enabled': llm_enabled,
            'active_llm': active_llm,
            'llm_status': llm_status,
            'conversation_history_length': len(chatbot.nlp_engine.llm.conversation_history) if llm_enabled else 0,
            'tts_methods': chatbot.tts_methods,
            'primary_tts': chatbot.primary_tts,
            'system_ready': True
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


@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """
    Analyze an uploaded image with the active LLM (OpenAI vision recommended).
    Expects multipart/form-data with:
      - image: file
      - prompt: optional text prompt (defaults to generic description request)
    """
    try:
        if 'image' not in request.files:
            return jsonify({'status': 'error', 'message': 'No image file provided'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'status': 'error', 'message': 'Empty filename for image upload'}), 400

        prompt = request.form.get('prompt', 'Describe this image in detail.')
        image_bytes = image_file.read()

        if not image_bytes:
            return jsonify({'status': 'error', 'message': 'Uploaded image is empty'}), 400

        response_text = chatbot.nlp_engine.analyze_image(image_bytes, prompt)

        return jsonify({
            'status': 'success',
            'response': response_text
        })
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(
        debug=Config.DEBUG, 
        host=Config.HOST, 
        port=Config.PORT
    )
