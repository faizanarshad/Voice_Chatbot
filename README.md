# AI Voice Chatbot

A sophisticated voice-enabled chatbot powered by advanced Natural Language Processing (NLP) and speech recognition technologies. This application provides a modern, responsive web interface for voice and text interactions with an AI assistant.

## 🌟 Features

### Core Capabilities
- **Voice Recognition**: Real-time speech-to-text conversion using Google Speech Recognition
- **Text-to-Speech**: Natural-sounding voice responses with customizable settings
- **Advanced NLP**: Intent recognition, entity extraction, and sentiment analysis
- **Context Awareness**: Maintains conversation context and user preferences
- **Multi-modal Interface**: Both voice and text input/output support

### Intelligent Features
- **Intent Recognition**: Understands user intentions (greetings, weather, time, music, etc.)
- **Entity Extraction**: Identifies locations, times, numbers, and people from speech
- **Sentiment Analysis**: Analyzes user mood and adjusts responses accordingly
- **Conversation Memory**: Tracks conversation history and user preferences
- **Confidence Scoring**: Provides confidence levels for NLP analysis
- **LLM Integration**: Optional integration with OpenAI GPT, Anthropic Claude, or local Ollama models

### User Interface
- **Modern Design**: Beautiful, responsive web interface with glassmorphism effects
- **Real-time Updates**: Live status indicators and conversation flow
- **Voice Visualizer**: Animated audio visualization during voice input
- **Quick Actions**: One-click access to common functions
- **Settings Panel**: Customizable voice speed, volume, and preferences

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Microphone access
- Speakers/headphones
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Voice_Chatbot.git
   cd Voice_Chatbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys and preferences
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🤖 LLM Integration (Optional)

Enhance your chatbot with powerful Large Language Models for more intelligent and context-aware responses.

### Quick LLM Setup

Run the interactive setup script:
```bash
python setup_llm.py
```

### Supported LLM Providers

- **OpenAI GPT** (Recommended): Easy setup, high-quality responses
- **Anthropic Claude**: Excellent reasoning, safety-focused
- **Ollama**: Free local models, privacy-focused

### Manual Configuration

1. **Copy environment template:**
   ```bash
   cp env_example.txt .env
   ```

2. **Edit .env file:**
   ```env
   USE_LLM=true
   ACTIVE_LLM=openai  # or anthropic, ollama
   OPENAI_API_KEY=your-api-key-here
   ```

3. **Restart the application:**
   ```bash
   python app.py
   ```

For detailed setup instructions, see [LLM_SETUP.md](LLM_SETUP.md).

## 📁 Project Structure

```
Voice_Chatbot/
├── app.py                 # Main Flask application
├── nlp_engine.py          # Advanced NLP processing engine
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env.example          # Environment variables template
├── templates/
│   └── index.html        # Main web interface
└── static/
    ├── css/
    │   └── style.css     # Modern styling
    └── js/
        └── app.js        # Frontend JavaScript logic
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Flask Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
HOST=0.0.0.0
PORT=5000

# Speech Recognition
SPEECH_RECOGNITION_TIMEOUT=5
SPEECH_RECOGNITION_PHRASE_TIME_LIMIT=10
SPEECH_RECOGNITION_AMBIENT_NOISE_DURATION=1

# Text-to-Speech
TTS_RATE=150
TTS_VOLUME=0.9
TTS_VOICE_ID=

# NLP Settings
NLP_CONFIDENCE_THRESHOLD=0.7
NLP_MAX_CONVERSATION_HISTORY=50

# Optional API Keys (for enhanced features)
OPENAI_API_KEY=
WEATHER_API_KEY=
NEWS_API_KEY=

# Logging
LOG_LEVEL=INFO
LOG_FILE=voice_chatbot.log
```

### Feature Flags

Control which features are enabled:

```env
ENABLE_VOICE_RECOGNITION=True
ENABLE_TEXT_TO_SPEECH=True
ENABLE_ADVANCED_NLP=True
ENABLE_WEATHER_API=False
ENABLE_NEWS_API=False
```

## 🎯 Usage

### Voice Interaction
1. Click the "Start Voice" button
2. Speak clearly into your microphone
3. The chatbot will process your speech and respond
4. Click "Stop Voice" to end voice recognition

### Text Interaction
1. Type your message in the text input field
2. Press Enter or click the send button
3. Receive instant AI responses

### Quick Actions
Use the sidebar quick action buttons for common tasks:
- **Time**: Get current time
- **Weather**: Weather information
- **Joke**: Tell a joke
- **Help**: Learn about capabilities

### Settings
Adjust voice settings in the sidebar:
- **Speed**: Control speech rate (0.5x - 2x)
- **Volume**: Adjust audio volume (0% - 100%)

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - Main web interface
- `POST /api/start-listening` - Start voice recognition
- `POST /api/stop-listening` - Stop voice recognition
- `POST /api/process-text` - Process text input
- `POST /api/speak` - Convert text to speech

### Analytics & Management
- `GET /api/status` - Get chatbot status
- `GET /api/conversation-history` - Get conversation history
- `GET /api/conversation-summary` - Get analytics summary
- `GET/POST /api/user-preferences` - Manage user preferences
- `POST /api/nlp-analysis` - Analyze text with NLP

## 🧠 NLP Capabilities

### Intent Recognition
The chatbot recognizes various user intents:
- **Greeting**: Hello, hi, hey, good morning
- **Farewell**: Goodbye, bye, see you
- **Weather**: Weather, temperature, forecast
- **Time**: Time, clock, what time is it
- **Help**: Help, what can you do
- **Music**: Music, play, song, artist
- **News**: News, headlines, current events
- **Joke**: Joke, funny, humor
- **Search**: Search, find, look up
- **Reminder**: Remind, reminder, set alarm
- **Calculation**: Calculate, math, compute

### Entity Extraction
Automatically identifies:
- **Locations**: Cities, places, addresses
- **Time Entities**: Today, tomorrow, next week
- **Numbers**: Quantities, amounts, measurements
- **People**: Names, contacts

### Sentiment Analysis
Analyzes user sentiment and adjusts responses:
- **Positive**: Enthusiastic, happy, satisfied
- **Negative**: Frustrated, sad, angry
- **Neutral**: Balanced, indifferent

## 🎨 Customization

### Adding New Intents
1. Edit `nlp_engine.py`
2. Add patterns to `_load_intent_patterns()`
3. Add responses to `_get_base_response()`

### Custom Voice Settings
1. Modify TTS settings in `config.py`
2. Adjust speech recognition parameters
3. Configure voice preferences

### UI Customization
1. Edit `static/css/style.css` for styling
2. Modify `templates/index.html` for layout
3. Update `static/js/app.js` for functionality

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set `DEBUG=False` in environment
2. Configure proper `SECRET_KEY`
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Set up reverse proxy (Nginx, Apache)

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🔍 Troubleshooting

### Common Issues

**Microphone not working:**
- Check microphone permissions
- Ensure microphone is not muted
- Try different microphone input

**Speech recognition errors:**
- Check internet connection (required for Google Speech Recognition)
- Speak clearly and slowly
- Reduce background noise

**Text-to-speech issues:**
- Check speaker/headphone connections
- Verify audio output settings
- Adjust TTS volume in settings

**Installation problems:**
- Ensure Python 3.8+ is installed
- Use virtual environment
- Install system audio dependencies (portaudio)

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**macOS:**
```bash
brew install portaudio
```

**Windows:**
- PyAudio should install automatically with pip

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Speech Recognition API
- pyttsx3 for text-to-speech
- Flask web framework
- Modern CSS and JavaScript libraries

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the configuration options

---

**Happy chatting! 🎉**