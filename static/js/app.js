class VoiceChatbot {
    constructor() {
        this.isListening = false;
        this.conversationHistory = [];
        this.recordingTimer = null;
        this.recordingStartTime = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateStats();
        this.loadSettings();
    }

    bindEvents() {
        // Text input handling
        const textInput = document.getElementById('text-input');
        const sendBtn = document.getElementById('send-btn');

        textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendTextMessage();
            }
        });

        sendBtn.addEventListener('click', () => {
            this.sendTextMessage();
        });

        // Voice controls
        const voiceBtn = document.getElementById('voice-btn');
        const stopVoiceBtn = document.getElementById('stop-voice-btn');

        voiceBtn.addEventListener('click', () => {
            this.startVoiceListening();
        });

        stopVoiceBtn.addEventListener('click', () => {
            this.stopVoiceListening();
        });

        // Quick action buttons
        const quickActionBtns = document.querySelectorAll('.quick-action-btn');
        quickActionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this.handleQuickAction(action);
            });
        });

        // Settings
        const voiceSpeed = document.getElementById('voice-speed');
        const voiceVolume = document.getElementById('voice-volume');

        voiceSpeed.addEventListener('input', (e) => {
            this.updateSpeedDisplay(e.target.value);
        });

        voiceVolume.addEventListener('input', (e) => {
            this.updateVolumeDisplay(e.target.value);
        });
    }

    async sendTextMessage() {
        const textInput = document.getElementById('text-input');
        const message = textInput.value.trim();

        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        textInput.value = '';

        try {
            const response = await fetch('/api/process-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: message })
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.addMessage(data.response, 'bot');
                this.conversationHistory = data.conversation_history || [];
                this.updateStats();
            } else {
                this.addMessage('Sorry, I encountered an error processing your message.', 'bot');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    }

    async startVoiceListening() {
        if (this.isListening) return;

        try {
            const response = await fetch('/api/start-listening', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.isListening = true;
                this.updateVoiceUI(true);
                this.showVisualizer(true);
                this.updateStatus('Listening...', 'listening');
                this.startRecordingTimer();
            } else {
                this.showNotification('Error starting voice recognition', 'error');
            }
        } catch (error) {
            console.error('Error starting voice listening:', error);
            this.showNotification('Error starting voice recognition', 'error');
        }
    }

    async stopVoiceListening() {
        if (!this.isListening) return;

        // Stop timer immediately when stop button is clicked
        this.stopRecordingTimer();
        this.isListening = false;
        this.updateVoiceUI(false);
        this.showVisualizer(false);
        this.updateStatus('Ready', 'ready');

        try {
            const response = await fetch('/api/stop-listening', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (data.status !== 'success') {
                this.showNotification('Error stopping voice recognition', 'error');
            }
        } catch (error) {
            console.error('Error stopping voice listening:', error);
            this.showNotification('Error stopping voice recognition', 'error');
        }
    }

    async handleQuickAction(action) {
        const actions = {
            'time': 'What time is it?',
            'weather': 'What\'s the weather like?',
            'joke': 'Tell me a joke',
            'help': 'What can you do?'
        };

        const message = actions[action];
        if (message) {
            this.addMessage(message, 'user');
            
            try {
                const response = await fetch('/api/process-text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: message })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    this.addMessage(data.response, 'bot');
                    this.conversationHistory = data.conversation_history || [];
                    this.updateStats();
                } else {
                    this.addMessage('Sorry, I encountered an error processing your request.', 'bot');
                }
            } catch (error) {
                console.error('Error handling quick action:', error);
                this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        }
    }

    addMessage(text, sender) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        if (sender === 'bot') {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
        } else {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        }

        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = `<p>${this.escapeHtml(text)}</p>`;

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Update message count
        this.updateStats();
    }

    updateVoiceUI(listening) {
        const voiceBtn = document.getElementById('voice-btn');
        const stopVoiceBtn = document.getElementById('stop-voice-btn');

        if (listening) {
            voiceBtn.style.display = 'none';
            stopVoiceBtn.style.display = 'flex';
            voiceBtn.classList.add('listening');
        } else {
            voiceBtn.style.display = 'flex';
            stopVoiceBtn.style.display = 'none';
            voiceBtn.classList.remove('listening');
        }
    }

    showVisualizer(show) {
        const visualizer = document.getElementById('voice-visualizer');
        if (show) {
            visualizer.classList.add('active');
        } else {
            visualizer.classList.remove('active');
        }
    }

    updateStatus(text, type) {
        const statusText = document.getElementById('status-text');
        const statusDot = document.getElementById('status-dot');
        const listeningStatus = document.getElementById('listening-status');

        statusText.textContent = text;
        listeningStatus.textContent = text;

        // Update status dot
        statusDot.className = 'status-dot';
        if (type === 'listening') {
            statusDot.classList.add('listening');
        } else if (type === 'error') {
            statusDot.classList.add('error');
        }
    }

    updateStats() {
        const messageCount = document.getElementById('message-count');
        const totalMessages = this.conversationHistory.length;
        messageCount.textContent = totalMessages;
    }

    updateSpeedDisplay(value) {
        const speedValue = document.getElementById('speed-value');
        speedValue.textContent = `${value}x`;
    }

    updateVolumeDisplay(value) {
        const volumeValue = document.getElementById('volume-value');
        volumeValue.textContent = `${Math.round(value * 100)}%`;
    }

    loadSettings() {
        // Load saved settings from localStorage
        const savedSpeed = localStorage.getItem('voiceSpeed') || '1';
        const savedVolume = localStorage.getItem('voiceVolume') || '0.9';

        document.getElementById('voice-speed').value = savedSpeed;
        document.getElementById('voice-volume').value = savedVolume;

        this.updateSpeedDisplay(savedSpeed);
        this.updateVolumeDisplay(savedVolume);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
            background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Poll for status updates
    startStatusPolling() {
        setInterval(async () => {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();

                if (data.status === 'success') {
                    if (data.is_listening !== this.isListening) {
                        this.isListening = data.is_listening;
                        this.updateVoiceUI(data.is_listening);
                        this.showVisualizer(data.is_listening);
                        this.updateStatus(
                            data.is_listening ? 'Listening...' : 'Ready',
                            data.is_listening ? 'listening' : 'ready'
                        );
                    }
                }
            } catch (error) {
                console.error('Error polling status:', error);
            }
        }, 2000);
    }

    // Recording timer methods
    startRecordingTimer() {
        this.recordingStartTime = Date.now();
        this.showRecordingTimer();
        this.updateTimer();
    }

    stopRecordingTimer() {
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
        this.hideRecordingTimer();
    }

    showRecordingTimer() {
        const timerElement = document.getElementById('recording-timer');
        if (timerElement) {
            timerElement.style.display = 'flex';
        }
    }

    hideRecordingTimer() {
        const timerElement = document.getElementById('recording-timer');
        if (timerElement) {
            timerElement.style.display = 'none';
        }
        const timerDisplay = document.getElementById('timer-display');
        if (timerDisplay) {
            timerDisplay.textContent = '00:00';
        }
    }

    updateTimer() {
        this.recordingTimer = setInterval(() => {
            if (this.recordingStartTime) {
                const elapsed = Date.now() - this.recordingStartTime;
                const minutes = Math.floor(elapsed / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                
                const timerDisplay = document.getElementById('timer-display');
                if (timerDisplay) {
                    timerDisplay.textContent = timeString;
                }
            }
        }, 1000);
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.voiceChatbot = new VoiceChatbot();
    window.voiceChatbot.startStatusPolling();
});

// Add CSS animations for notifications
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

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
