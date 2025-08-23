# LLM Integration Setup Guide

This guide will help you integrate Large Language Models (LLMs) with your voice chatbot to significantly enhance its capabilities.

## 🚀 Available LLM Options

### 1. OpenAI GPT (Recommended for beginners)
- **Models**: GPT-3.5-turbo, GPT-4
- **Pros**: Easy setup, high quality responses, reliable
- **Cons**: Requires API key, usage costs
- **Best for**: Production use, high-quality conversations

### 2. Anthropic Claude
- **Models**: Claude-3-Haiku, Claude-3-Sonnet, Claude-3-Opus
- **Pros**: Excellent reasoning, safety-focused, high quality
- **Cons**: Requires API key, usage costs
- **Best for**: Professional use, complex reasoning tasks

### 3. Ollama (Local LLMs)
- **Models**: Llama2, Mistral, CodeLlama, and many more
- **Pros**: Free, private, no internet required
- **Cons**: Requires local setup, hardware resources
- **Best for**: Privacy-focused use, offline operation

## 📋 Setup Instructions

### Step 1: Choose Your LLM Provider

#### Option A: OpenAI GPT (Easiest)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and get your API key
3. Add to your `.env` file:
   ```bash
   USE_LLM=true
   ACTIVE_LLM=openai
   OPENAI_API_KEY=your-api-key-here
   ```

#### Option B: Anthropic Claude
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account and get your API key
3. Add to your `.env` file:
   ```bash
   USE_LLM=true
   ACTIVE_LLM=anthropic
   ANTHROPIC_API_KEY=your-api-key-here
   ```

#### Option C: Ollama (Local)
1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Pull a model: `ollama pull llama2`
3. Add to your `.env` file:
   ```bash
   USE_LLM=true
   ACTIVE_LLM=ollama
   OLLAMA_MODEL=llama2
   ```

### Step 2: Configure Environment

1. Copy the example environment file:
   ```bash
   cp env_example.txt .env
   ```

2. Edit `.env` and add your LLM configuration:
   ```bash
   # Enable LLM
   USE_LLM=true
   ACTIVE_LLM=openai  # or anthropic, ollama
   
   # Add your API key
   OPENAI_API_KEY=sk-your-key-here
   ```

### Step 3: Test the Integration

1. Restart your Flask application:
   ```bash
   python app.py
   ```

2. Test with a complex query:
   ```bash
   curl -X POST http://localhost:5001/api/process-text \
     -H "Content-Type: application/json" \
     -d '{"text": "Explain quantum computing in simple terms"}'
   ```

## 🔧 Advanced Configuration

### Custom System Prompts

You can customize the AI's behavior by modifying the system prompts in `nlp_engine.py`:

```python
system_prompt = """You are a helpful AI voice assistant specialized in:
- Technical explanations
- Creative writing
- Problem solving
- Educational content

Keep responses conversational and engaging for voice interaction."""
```

### Model Selection

#### OpenAI Models
- `gpt-3.5-turbo` (fast, cost-effective)
- `gpt-4` (highest quality, more expensive)
- `gpt-4-turbo` (balanced)

#### Anthropic Models
- `claude-3-haiku-20240307` (fast, cost-effective)
- `claude-3-sonnet-20240229` (balanced)
- `claude-3-opus-20240229` (highest quality)

#### Ollama Models
- `llama2` (general purpose)
- `mistral` (good reasoning)
- `codellama` (programming focused)
- `llama2-uncensored` (less filtered)

### Response Customization

Modify the LLM parameters in `nlp_engine.py`:

```python
data = {
    'model': 'gpt-3.5-turbo',
    'messages': messages,
    'max_tokens': 200,      # Longer responses
    'temperature': 0.8,     # More creative
    'top_p': 0.9,          # More focused
    'frequency_penalty': 0.1,  # Reduce repetition
    'presence_penalty': 0.1    # Encourage new topics
}
```

## 🎯 Use Cases

### 1. Educational Assistant
```python
system_prompt = """You are an educational AI assistant. Help users learn by:
- Explaining complex concepts simply
- Providing examples and analogies
- Asking follow-up questions
- Encouraging critical thinking"""
```

### 2. Creative Writing Assistant
```python
system_prompt = """You are a creative writing assistant. Help users by:
- Brainstorming ideas
- Improving writing style
- Suggesting plot developments
- Providing constructive feedback"""
```

### 3. Technical Support
```python
system_prompt = """You are a technical support assistant. Help users by:
- Troubleshooting problems step-by-step
- Explaining technical concepts
- Providing code examples
- Suggesting best practices"""
```

## 🔒 Security & Privacy

### API Key Security
- Never commit API keys to version control
- Use environment variables
- Rotate keys regularly
- Monitor usage to prevent abuse

### Privacy Considerations
- **OpenAI/Anthropic**: Data may be used for training
- **Ollama**: Completely private, runs locally
- Consider data retention policies

## 💰 Cost Management

### OpenAI Pricing (per 1K tokens)
- GPT-3.5-turbo: $0.0015 input, $0.002 output
- GPT-4: $0.03 input, $0.06 output

### Anthropic Pricing (per 1K tokens)
- Claude-3-Haiku: $0.00025 input, $0.00125 output
- Claude-3-Sonnet: $0.003 input, $0.015 output

### Ollama
- Free to use
- Requires local hardware resources

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify your API key is correct
   - Check account has sufficient credits
   - Ensure key has proper permissions

2. **Rate Limiting**
   - Implement exponential backoff
   - Use request queuing
   - Monitor usage limits

3. **Ollama Connection Issues**
   - Ensure Ollama is running: `ollama serve`
   - Check model is downloaded: `ollama list`
   - Verify port 11434 is accessible

4. **Response Quality Issues**
   - Adjust temperature (0.0-1.0)
   - Modify max_tokens
   - Refine system prompts
   - Add conversation context

### Debug Mode

Enable detailed logging by setting:
```bash
LOG_LEVEL=DEBUG
```

## 📈 Performance Optimization

### Response Time
- Use faster models for real-time interaction
- Implement response caching
- Optimize prompt length

### Cost Optimization
- Use appropriate model sizes
- Implement token counting
- Cache common responses
- Use local models for privacy-sensitive tasks

## 🔄 Fallback Strategy

The system automatically falls back to built-in responses when:
- LLM is not configured
- API calls fail
- Rate limits are exceeded
- Network issues occur

This ensures your chatbot always responds, even when LLM services are unavailable.

## 🎉 Next Steps

1. **Start Simple**: Begin with OpenAI GPT-3.5-turbo
2. **Test Thoroughly**: Try various conversation types
3. **Monitor Usage**: Track costs and performance
4. **Iterate**: Refine prompts and parameters
5. **Scale**: Consider local models for production

Your voice chatbot is now ready to provide intelligent, context-aware responses powered by state-of-the-art language models! 🚀

