"""
API routes and endpoints for AI Voice Assistant Pro
"""

from flask import request, jsonify, render_template
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def register_routes(app, chatbot):
    """Register all API routes with the Flask app"""
    
    @app.route('/')
    def index():
        """Serve the main web interface"""
        return render_template('index.html')
    
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
    
    @app.route('/api/process-text', methods=['POST'])
    def process_text():
        """Process text input and generate AI response"""
        try:
            data = request.get_json()
            user_input = data.get('text', '').strip()
            user_id = data.get('user_id', 'default')
            
            if not user_input:
                return jsonify({'error': 'No text provided'}), 400
            
            # Process with NLP engine
            response = chatbot.process_nlp(user_input, user_id)
            
            return jsonify({
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            })
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/process-audio', methods=['POST'])
    def process_audio():
        """Process audio input and generate AI response"""
        try:
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400
            
            audio_file = request.files['audio']
            user_id = request.form.get('user_id', 'default')
            
            if audio_file.filename == '':
                return jsonify({'error': 'No audio file selected'}), 400
            
            # Process audio with speech recognition
            text = chatbot.listen_for_speech_from_file(audio_file)
            
            if not text:
                return jsonify({'error': 'Could not process audio'}), 400
            
            # Process with NLP engine
            response = chatbot.process_nlp(text, user_id)
            
            return jsonify({
                'text': text,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            })
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/speak', methods=['POST'])
    def speak_text():
        """Convert text to speech"""
        try:
            data = request.get_json()
            text = data.get('text', '').strip()
            
            if not text:
                return jsonify({'error': 'No text provided'}), 400
            
            # Convert text to speech
            chatbot.speak(text)
            
            return jsonify({
                'status': 'success',
                'message': 'Speech completed',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/conversation-summary', methods=['GET'])
    def get_conversation_summary():
        """Get conversation history summary"""
        try:
            return jsonify({
                'conversation_count': len(chatbot.conversation_history),
                'recent_conversations': chatbot.conversation_history[-10:] if chatbot.conversation_history else [],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/features', methods=['GET'])
    def get_features():
        """Get available features and capabilities"""
        try:
            features = {
                'voice_recognition': True,
                'text_to_speech': True,
                'llm_integration': chatbot.nlp_engine.use_llm,
                'conversation_history': True,
                'intent_recognition': True,
                'sentiment_analysis': True,
                'multi_tts_methods': len(chatbot.tts_methods) > 1,
                'available_tts_methods': chatbot.tts_methods,
                'primary_tts_method': chatbot.primary_tts
            }
            
            return jsonify(features)
        except Exception as e:
            logger.error(f"Error getting features: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/start-listening', methods=['POST'])
    def start_listening():
        """Start voice listening session and return recognized text"""
        try:
            if chatbot.is_listening:
                return jsonify({
                    'status': 'success',
                    'message': 'Already listening',
                    'is_listening': True,
                    'timestamp': datetime.now().isoformat()
                })
            
            chatbot.is_listening = True
            
            # Listen for speech directly (blocking call)
            text = chatbot.listen_for_speech()
            
            if text:
                # Process with NLP engine
                response = chatbot.process_nlp(text)
                logger.info(f"🤖 Generated response: {response[:100]}...")
                
                # Speak the response aloud
                logger.info("🗣️ About to call TTS...")
                logger.info(f"🗣️ TTS Methods available: {chatbot.tts_methods}")
                logger.info(f"🗣️ Primary TTS method: {chatbot.primary_tts}")
                
                try:
                    chatbot.speak(response)
                    logger.info(f"✅ TTS completed successfully for response: {response[:50]}...")
                except Exception as tts_error:
                    logger.error(f"❌ TTS Error: {tts_error}")
                    logger.error(f"❌ TTS Error type: {type(tts_error)}")
                    logger.error(f"❌ TTS Error details: {str(tts_error)}")
                
                return jsonify({
                    'status': 'success',
                    'text': text,
                    'response': response,
                    'is_listening': False,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'status': 'success',
                    'message': 'No speech detected',
                    'is_listening': False,
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            logger.error(f"Error starting listening: {e}")
            chatbot.is_listening = False
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stop-listening', methods=['POST'])
    def stop_listening():
        """Stop voice listening session"""
        try:
            chatbot.is_listening = False
            
            return jsonify({
                'status': 'success',
                'message': 'Stopped listening',
                'is_listening': False,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error stopping listening: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/listen', methods=['POST'])
    def listen_for_voice():
        """Listen for voice input and return transcribed text"""
        try:
            if not chatbot.is_listening:
                chatbot.is_listening = True
            
            # Listen for speech
            text = chatbot.listen_for_speech()
            
            if text:
                # Process with NLP engine
                response = chatbot.process_nlp(text)
                
                return jsonify({
                    'text': text,
                    'response': response,
                    'is_listening': False,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'error': 'Could not understand speech',
                    'is_listening': False,
                    'timestamp': datetime.now().isoformat()
                }), 400
                
        except Exception as e:
            logger.error(f"Error in voice listening: {e}")
            chatbot.is_listening = False
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/process-voice', methods=['POST'])
    def process_voice():
        """Process voice input directly without file upload"""
        try:
            # Listen for speech directly
            text = chatbot.listen_for_speech()
            
            if text:
                # Process with NLP engine
                response = chatbot.process_nlp(text)
                
                return jsonify({
                    'text': text,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'error': 'Could not understand speech',
                    'timestamp': datetime.now().isoformat()
                }), 400
                
        except Exception as e:
            logger.error(f"Error in voice processing: {e}")
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

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
