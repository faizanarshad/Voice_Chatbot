#!/bin/bash

# AI Voice Assistant Pro - Deployment Script
# This script helps deploy the application using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="ai-voice-assistant-pro"
CONTAINER_NAME="ai-voice-assistant-pro"
IMAGE_NAME="voice-chatbot"
PORT="5001"

echo -e "${BLUE}🚀 AI Voice Assistant Pro - Deployment Script${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f "config/development/env_example.txt" ]; then
            cp config/development/env_example.txt .env
            print_warning "Please edit .env file with your API keys before deploying"
            read -p "Press Enter to continue after editing .env file..."
        else
            print_error "No .env template found. Please create .env file manually."
            exit 1
        fi
    fi
    print_status ".env file found"
}

# Create necessary directories
create_directories() {
    mkdir -p logs temp
    print_status "Created necessary directories"
}

# Build Docker image
build_image() {
    print_info "Building Docker image..."
    docker-compose -f deployment/docker/docker-compose.yml build --no-cache
    print_status "Docker image built successfully"
}

# Deploy application
deploy_app() {
    print_info "Deploying application..."
    
    # Stop existing containers
    docker-compose -f deployment/docker/docker-compose.yml down 2>/dev/null || true
    
    # Start the application
    docker-compose -f deployment/docker/docker-compose.yml up -d
    
    print_status "Application deployed successfully"
}

# Check application health
check_health() {
    print_info "Checking application health..."
    
    # Wait for application to start
    sleep 10
    
    # Check if container is running
    if docker ps | grep -q $CONTAINER_NAME; then
        print_status "Container is running"
    else
        print_error "Container failed to start"
        docker-compose -f deployment/docker/docker-compose.yml logs
        exit 1
    fi
    
    # Check health endpoint
    if curl -f http://localhost:$PORT/api/status &>/dev/null; then
        print_status "Application is healthy and responding"
    else
        print_warning "Application may still be starting up. Check logs with: docker-compose -f deployment/docker/docker-compose.yml logs -f"
    fi
}

# Show application info
show_info() {
    echo ""
    echo -e "${BLUE}📱 Application Information:${NC}"
    echo "================================"
    echo "🌐 Web Interface: http://localhost:$PORT"
    echo "🔧 API Status: http://localhost:$PORT/api/status"
    echo "📊 API Features: http://localhost:$PORT/api/features"
    echo ""
    echo -e "${BLUE}🐳 Docker Commands:${NC}"
    echo "===================="
    echo "View logs: docker-compose -f deployment/docker/docker-compose.yml logs -f"
    echo "Stop app:  docker-compose -f deployment/docker/docker-compose.yml down"
    echo "Restart:   docker-compose -f deployment/docker/docker-compose.yml restart"
    echo "Shell:     docker-compose -f deployment/docker/docker-compose.yml exec voice-chatbot bash"
    echo ""
}

# Cleanup function
cleanup() {
    print_info "Cleaning up..."
    docker-compose -f deployment/docker/docker-compose.yml down
    print_status "Cleanup completed"
}

# Main deployment function
main() {
    case "${1:-deploy}" in
        "deploy")
            check_docker
            check_env
            create_directories
            build_image
            deploy_app
            check_health
            show_info
            ;;
        "stop")
            cleanup
            ;;
        "restart")
            check_docker
            deploy_app
            check_health
            show_info
            ;;
        "logs")
            docker-compose -f deployment/docker/docker-compose.yml logs -f
            ;;
        "shell")
            docker-compose -f deployment/docker/docker-compose.yml exec voice-chatbot bash
            ;;
        "status")
            docker-compose -f deployment/docker/docker-compose.yml ps
            ;;
        "clean")
            print_info "Removing all containers and images..."
            docker-compose -f deployment/docker/docker-compose.yml down -v --rmi all
            print_status "Cleanup completed"
            ;;
        *)
            echo "Usage: $0 {deploy|stop|restart|logs|shell|status|clean}"
            echo ""
            echo "Commands:"
            echo "  deploy  - Deploy the application (default)"
            echo "  stop    - Stop the application"
            echo "  restart - Restart the application"
            echo "  logs    - Show application logs"
            echo "  shell   - Open shell in container"
            echo "  status  - Show container status"
            echo "  clean   - Remove all containers and images"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"