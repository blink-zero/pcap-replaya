#!/bin/bash

# PCAP Replaya Quick Deploy Script
# This script downloads and runs PCAP Replaya using pre-built Docker images

set -e

echo "🚀 PCAP Replaya Quick Deploy"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script requires root privileges for network interface access."
    echo "   Please run with sudo: sudo $0"
    exit 1
fi

# Create deployment directory
DEPLOY_DIR="pcap-replaya-deploy"
echo "📁 Creating deployment directory: $DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

# Download production docker-compose file
echo "📥 Downloading production configuration..."
curl -sSL https://raw.githubusercontent.com/blink-zero/pcap-replaya/main/docker-compose.prod.yml -o docker-compose.yml

# Download environment template
curl -sSL https://raw.githubusercontent.com/blink-zero/pcap-replaya/main/.env.example -o .env.example

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating environment configuration..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | xxd -p -c 32)
    sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    echo "✅ Generated secure secret key"
fi

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker-compose pull

# Start the application
echo "🚀 Starting PCAP Replaya..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ PCAP Replaya is now running!"
    echo ""
    echo "🌐 Access the application at:"
    echo "   http://localhost"
    echo "   http://$(hostname -I | awk '{print $1}')"
    echo ""
    echo "📊 Check status: docker-compose ps"
    echo "📋 View logs: docker-compose logs -f"
    echo "🛑 Stop: docker-compose down"
    echo ""
    echo "📚 Documentation: https://github.com/blink-zero/pcap-replaya"
else
    echo "❌ Failed to start services. Check logs with: docker-compose logs"
    exit 1
fi
