# 📁 Project Structure

This document describes the professional project structure of AI Voice Assistant Pro.

## 🏗️ Directory Layout

```
Voice_Chatbot/
├── 📁 src/                          # Source code package
│   └── 📁 voice_chatbot/            # Main application package
│       ├── 📁 core/                 # Core functionality
│       │   ├── __init__.py
│       │   ├── app.py              # Main VoiceChatbot class
│       │   └── config.py           # Configuration management
│       ├── 📁 services/             # Business logic services
│       │   ├── __init__.py
│       │   └── nlp_engine.py       # NLP and LLM processing
│       ├── 📁 api/                  # API endpoints and routes
│       │   ├── __init__.py
│       │   └── routes.py           # Flask route definitions
│       ├── 📁 models/               # Data models (future)
│       │   └── __init__.py
│       ├── 📁 utils/                # Utility functions (future)
│       │   └── __init__.py
│       └── __init__.py
├── 📁 web/                          # Web assets
│   ├── 📁 static/                   # Static files (CSS, JS, images)
│   │   ├── 📁 css/
│   │   └── 📁 js/
│   └── 📁 templates/                # HTML templates
│       └── index.html
├── 📁 tests/                        # Test suite
│   ├── 📁 unit/                     # Unit tests
│   ├── 📁 integration/              # Integration tests
│   ├── test_app.py                  # Main application tests
│   └── test_llm_direct.py          # LLM functionality tests
├── 📁 docs/                         # Documentation
│   ├── 📁 api/                      # API documentation
│   ├── 📁 deployment/               # Deployment guides
│   └── 📁 development/              # Development guides
├── 📁 scripts/                      # Utility scripts
│   ├── deploy.sh                    # Deployment script
│   └── nginx.conf                   # Nginx configuration
├── 📁 deployment/                   # Deployment configurations
│   └── 📁 docker/                   # Docker files
│       ├── Dockerfile
│       ├── docker-compose.yml
│       └── .dockerignore
├── 📁 config/                       # Configuration files
│   └── 📁 development/              # Development configs
│       ├── env_example.txt
│       └── env.production.txt
├── 📁 logs/                         # Application logs
│   └── voice_chatbot.log
├── 📁 temp/                         # Temporary files
├── main.py                          # Application entry point
├── setup.py                         # Package setup
├── pyproject.toml                   # Modern Python packaging
├── MANIFEST.in                      # Package manifest
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
├── .dockerignore                    # Docker ignore rules
└── README.md                        # Project documentation
```

## 📦 Package Structure

### Core Package (`src/voice_chatbot/`)

The main application package containing all business logic and functionality.

#### Core Module (`core/`)
- **`app.py`**: Main `VoiceChatbot` class with speech recognition and TTS
- **`config.py`**: Configuration management and environment variables

#### Services Module (`services/`)
- **`nlp_engine.py`**: NLP processing, LLM integration, and response generation

#### API Module (`api/`)
- **`routes.py`**: Flask route definitions and API endpoints

#### Models Module (`models/`)
- Reserved for future data models and database schemas

#### Utils Module (`utils/`)
- Reserved for future utility functions and helpers

## 🌐 Web Assets (`web/`)

### Static Files (`web/static/`)
- **CSS**: Styling and themes
- **JavaScript**: Frontend functionality and API interactions
- **Images**: Icons, logos, and media assets

### Templates (`web/templates/`)
- **HTML templates**: Jinja2 templates for rendering pages

## 🧪 Testing (`tests/`)

### Test Organization
- **`unit/`**: Unit tests for individual components
- **`integration/`**: Integration tests for component interactions
- **`test_app.py`**: Main application functionality tests
- **`test_llm_direct.py`**: LLM integration tests

## 📚 Documentation (`docs/`)

### Documentation Structure
- **`api/`**: API documentation and specifications
- **`deployment/`**: Deployment guides and configurations
- **`development/`**: Development setup and contribution guides

## 🚀 Deployment (`deployment/`)

### Docker Deployment (`deployment/docker/`)
- **`Dockerfile`**: Container image definition
- **`docker-compose.yml`**: Multi-container orchestration
- **`.dockerignore`**: Docker build optimization

## ⚙️ Configuration (`config/`)

### Environment Configurations
- **`development/`**: Development environment settings
- **`production/`**: Production environment settings

## 🛠️ Scripts (`scripts/`)

### Utility Scripts
- **`deploy.sh`**: Automated deployment script
- **`nginx.conf`**: Production web server configuration

## 📋 Key Files

### Entry Points
- **`main.py`**: Main application entry point
- **`setup.py`**: Traditional Python package setup
- **`pyproject.toml`**: Modern Python packaging configuration

### Configuration
- **`requirements.txt`**: Python package dependencies
- **`.gitignore`**: Git version control exclusions
- **`.dockerignore`**: Docker build exclusions
- **`MANIFEST.in`**: Package distribution files

## 🔄 Import Structure

### Internal Imports
```python
# Core imports
from voice_chatbot.core.app import VoiceChatbot
from voice_chatbot.core.config import Config

# Service imports
from voice_chatbot.services.nlp_engine import NLPEngine

# API imports
from voice_chatbot.api.routes import register_routes
```

### External Imports
```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party packages
from flask import Flask
from flask_cors import CORS
import speech_recognition as sr
```

## 🎯 Benefits of This Structure

### 1. **Modularity**
- Clear separation of concerns
- Easy to maintain and extend
- Reusable components

### 2. **Scalability**
- Easy to add new features
- Supports team development
- Professional industry standards

### 3. **Testing**
- Organized test structure
- Easy to write and run tests
- Comprehensive coverage

### 4. **Deployment**
- Docker-ready structure
- Multiple deployment options
- Production-ready configuration

### 5. **Documentation**
- Comprehensive documentation
- Clear project structure
- Easy onboarding for new developers

## 🚀 Getting Started

### Development Setup
```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Start development server
python main.py
```

### Production Deployment
```bash
# Docker deployment
./scripts/deploy.sh deploy

# Traditional deployment
pip install .
python main.py
```

This structure follows Python packaging best practices and provides a solid foundation for professional software development.
