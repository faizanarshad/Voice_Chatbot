# 🐳 Docker Deployment Guide

This guide explains how to deploy AI Voice Assistant Pro using Docker for consistent, scalable deployment across different environments.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB+ RAM available
- 5GB+ disk space

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd Voice_Chatbot
```

### 2. Configure Environment

```bash
# Copy environment template
cp env.production.txt .env

# Edit .env with your API keys
nano .env
```

**Required Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key for LLM features
- `SECRET_KEY`: Flask secret key for production

### 3. Deploy with Script

```bash
# Make script executable (if not already)
chmod +x deploy.sh

# Deploy the application
./deploy.sh deploy
```

### 4. Access Application

- **Web Interface**: http://localhost:5001
- **API Status**: http://localhost:5001/api/status
- **Health Check**: http://localhost:5001/health

## 🛠️ Manual Docker Commands

### Build and Run

```bash
# Build the image
docker-compose build

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Production Deployment

```bash
# Deploy with nginx reverse proxy
docker-compose --profile production up -d

# Scale the application
docker-compose up -d --scale voice-chatbot=3
```

## 📊 Container Management

### View Status

```bash
# Check container status
./deploy.sh status

# View logs
./deploy.sh logs

# Open shell in container
./deploy.sh shell
```

### Maintenance

```bash
# Restart application
./deploy.sh restart

# Stop application
./deploy.sh stop

# Clean up everything
./deploy.sh clean
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | production | Flask environment |
| `USE_LLM` | true | Enable LLM features |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `TTS_RATE` | 200 | Speech rate |
| `TTS_VOLUME` | 0.8 | Speech volume |
| `PORT` | 5001 | Application port |

### Docker Compose Services

- **voice-chatbot**: Main application container
- **nginx**: Reverse proxy (production profile)

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

## 🌐 Production Deployment

### With Nginx Reverse Proxy

```bash
# Deploy with nginx
docker-compose --profile production up -d

# Configure SSL certificates
mkdir ssl
# Add your cert.pem and key.pem files to ssl/ directory
# Uncomment HTTPS server block in nginx.conf
```

### Custom Domain

1. Update `nginx.conf` with your domain
2. Configure SSL certificates
3. Set up DNS records

### Scaling

```bash
# Scale to 3 instances
docker-compose up -d --scale voice-chatbot=3

# Load balancer will distribute requests
```

## 🔍 Monitoring and Logs

### Health Checks

```bash
# Check application health
curl http://localhost:5001/api/status

# Container health status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Log Management

```bash
# View real-time logs
docker-compose logs -f voice-chatbot

# View specific service logs
docker-compose logs -f nginx

# Export logs
docker-compose logs > logs/deployment.log
```

### Performance Monitoring

```bash
# Container resource usage
docker stats

# Detailed container info
docker inspect voice-chatbot
```

## 🛡️ Security Considerations

### Container Security

- Runs as non-root user
- No privileged access
- Security headers configured
- Rate limiting enabled

### Network Security

```bash
# Custom network isolation
docker network create voice-chatbot-network

# Firewall rules
ufw allow 5001/tcp
ufw allow 80/tcp
ufw allow 443/tcp
```

### Secrets Management

```bash
# Use Docker secrets for production
echo "your-secret-key" | docker secret create flask_secret_key -

# Reference in docker-compose.yml
secrets:
  - flask_secret_key
```

## 🔧 Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs voice-chatbot

# Check environment variables
docker-compose config
```

**TTS not working:**
```bash
# Check audio devices
docker-compose exec voice-chatbot ls /dev/snd/

# Test TTS manually
docker-compose exec voice-chatbot python -c "from app import chatbot; chatbot.speak('test')"
```

**Memory issues:**
```bash
# Check resource usage
docker stats

# Increase memory limits in docker-compose.yml
```

### Debug Mode

```bash
# Run in debug mode
FLASK_ENV=development docker-compose up

# Access container shell
docker-compose exec voice-chatbot bash
```

## 📈 Performance Optimization

### Multi-stage Build

The Dockerfile uses multi-stage builds for:
- Smaller production images
- Faster builds
- Better caching

### Resource Optimization

```yaml
# Optimize for production
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

### Caching Strategy

```dockerfile
# Layer caching optimization
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy with Docker
        run: |
          docker-compose build
          docker-compose up -d
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.0.x/deploying/)

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment variables
3. Ensure all prerequisites are met
4. Check GitHub issues for known problems

---

**Happy Deploying! 🎉**
