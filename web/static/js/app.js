// Global variables
let isListening = false;
let recordingTimer = null;
let startTime = null;
let mediaRecorder = null;
let audioChunks = [];
let stream = null;

// DOM elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const textInput = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');
const recordingTimerEl = document.getElementById('recordingTimer');
const timerDisplay = document.getElementById('timerDisplay');
const voiceStatus = document.getElementById('voiceStatus');
const statusText = document.getElementById('status-text');
const statusDot = document.getElementById('status-dot');
const conversation = document.getElementById('conversation');

// Feature cards
const featureCards = document.querySelectorAll('.feature-card');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Add event listeners
    startBtn.addEventListener('click', startVoiceListening);
    stopBtn.addEventListener('click', stopVoiceListening);
    sendBtn.addEventListener('click', sendTextMessage);
    textInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendTextMessage();
        }
    });

    // Add feature card interactions
    featureCards.forEach(card => {
        card.addEventListener('click', function() {
            const feature = this.dataset.feature;
            showFeatureInfo(feature);
        });
    });

    // Start status polling
    pollStatus();
}

// Voice listening functions
async function startVoiceListening() {
    if (isListening) return;
    
    try {
        // Request microphone access
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Initialize MediaRecorder
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        // Set up event handlers
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = () => {
            processAudioRecording();
        };
        
        isListening = true;
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-flex';
        
        // Show recording timer
        recordingTimerEl.style.display = 'flex';
        startTime = Date.now();
        updateTimer();
        recordingTimer = setInterval(updateTimer, 1000);
        
        // Update status
        updateStatus('listening', 'Listening...');
        voiceStatus.textContent = 'Listening... Speak now!';
        
        // Start recording
        mediaRecorder.start();
        
        // Make API call to start listening
        fetch('/api/start-listening', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Started listening:', data);
        })
        .catch(error => {
            console.error('Error starting listening:', error);
            stopVoiceListening();
        });
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        updateStatus('error', 'Microphone access denied');
        alert('Please allow microphone access to use voice features.');
    }
}

function stopVoiceListening() {
    if (!isListening) return;
    
    isListening = false;
    startBtn.style.display = 'inline-flex';
    stopBtn.style.display = 'none';
    
    // Stop recording
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }
    
    // Stop stream
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    
    // Hide recording timer immediately
    recordingTimerEl.style.display = 'none';
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
    
    // Update status
    updateStatus('processing', 'Processing...');
    voiceStatus.textContent = 'Processing your speech...';
    
    // Make API call to stop listening
    fetch('/api/stop-listening', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Stopped listening:', data);
        if (data.text) {
            addMessage('user', data.text);
            addMessage('bot', data.response);
            voiceStatus.textContent = 'Ready for next command';
            updateStatus('ready', 'Ready');
        }
    })
    .catch(error => {
        console.error('Error stopping listening:', error);
        voiceStatus.textContent = 'Error processing speech';
        updateStatus('ready', 'Ready');
    });
}

function processAudioRecording() {
    if (audioChunks.length === 0) {
        updateStatus('ready', 'Ready');
        voiceStatus.textContent = 'No audio recorded';
        return;
    }
    
    // Create audio blob
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    
    // Send audio to server for processing
    fetch('/api/process-audio', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.text && data.response) {
            addMessage('user', data.text);
            addMessage('bot', data.response);
            voiceStatus.textContent = 'Ready for next command';
            updateStatus('ready', 'Ready');
        } else if (data.error) {
            voiceStatus.textContent = 'Error: ' + data.error;
            updateStatus('ready', 'Ready');
        }
    })
    .catch(error => {
        console.error('Error processing audio:', error);
        voiceStatus.textContent = 'Error processing speech';
        updateStatus('ready', 'Ready');
    });
    
    // Reset audio chunks
    audioChunks = [];
}

function updateTimer() {
    if (!startTime) return;
    
    const elapsed = Date.now() - startTime;
    const seconds = Math.floor(elapsed / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Text message functions
function sendTextMessage() {
    const text = textInput.value.trim();
    if (!text) return;
    
    addMessage('user', text);
    textInput.value = '';
    
    // Update status
    updateStatus('processing', 'Processing...');
    
    // Send text to API
    fetch('/api/process-text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        addMessage('bot', data.response);
        updateStatus('ready', 'Ready');
    })
    .catch(error => {
        console.error('Error sending text:', error);
        addMessage('bot', 'Sorry, I encountered an error processing your request.');
        updateStatus('ready', 'Ready');
    });
}

// Message display functions
function addMessage(sender, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    
    if (sender === 'user') {
        avatar.innerHTML = '<i class="fas fa-user"></i>';
    } else {
        avatar.innerHTML = '<i class="fas fa-robot"></i>';
    }
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.innerHTML = formatMessage(content);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    conversation.appendChild(messageDiv);
    
    // Scroll to bottom
    conversation.scrollTop = conversation.scrollHeight;
    
    // Remove welcome message if it exists
    const welcomeMessage = conversation.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
}

function formatMessage(content) {
    // Convert markdown-like formatting to HTML
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

// Status management
function updateStatus(status, text) {
    statusText.textContent = text;
    statusDot.className = `status-dot ${status}`;
}

function pollStatus() {
    setInterval(() => {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'listening' && !isListening) {
                    // Server thinks it's listening but we're not
                    stopVoiceListening();
                }
            })
            .catch(error => {
                console.error('Status poll error:', error);
            });
    }, 2000);
}

// Feature interactions
function showFeatureInfo(feature) {
    const featureNames = {
        'music_control': 'Music Control',
        'calendar': 'Calendar Management',
        'weather_detailed': 'Weather Information',
        'news_category': 'News Updates',
        'calculator_advanced': 'Advanced Calculator',
        'notes': 'Note Taking',
        'tasks': 'Task Management',
        'web_search': 'Web Search'
    };
    
    const featureDescriptions = {
        'music_control': 'Control your music playback, adjust volume, skip tracks, and manage playlists with voice commands.',
        'calendar': 'Schedule meetings, set reminders, check availability, and manage your calendar efficiently.',
        'weather_detailed': 'Get comprehensive weather forecasts, air quality data, UV index, and severe weather alerts.',
        'news_category': 'Access categorized news from world, technology, sports, business, and entertainment sources.',
        'calculator_advanced': 'Perform scientific calculations, statistical analysis, and complex mathematical operations.',
        'notes': 'Create, organize, and manage voice notes with categories and priority levels.',
        'tasks': 'Track tasks, set deadlines, manage projects, and maintain organized to-do lists.',
        'web_search': 'Search the internet, research topics, and find information from reliable sources.'
    };
    
    const featureName = featureNames[feature] || 'Feature';
    const description = featureDescriptions[feature] || 'This feature helps you with various tasks.';
    
    // Add a demo message for the feature
    addMessage('bot', `🎯 **${featureName}**\n\n${description}\n\nTry saying something like:\n• "Show me ${featureName.toLowerCase()}"\n• "Help me with ${featureName.toLowerCase()}"\n• "What can you do with ${featureName.toLowerCase()}?"`);
    
    // Highlight the feature card
    featureCards.forEach(card => {
        if (card.dataset.feature === feature) {
            card.style.borderColor = '#667eea';
            card.style.transform = 'scale(1.05)';
            setTimeout(() => {
                card.style.borderColor = 'transparent';
                card.style.transform = 'scale(1)';
            }, 2000);
        }
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
    `;
    
    if (type === 'success') {
        notification.style.background = '#10b981';
    } else if (type === 'error') {
        notification.style.background = '#ef4444';
    } else {
        notification.style.background = '#3b82f6';
    }
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
