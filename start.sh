#!/bin/bash

# PCAP Replaya Startup Script
# This script helps start the application with proper permissions

set -e

echo "🚀 Starting PCAP Replaya..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if running as root (required for network interface access)
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This application requires root privileges for network interface access."
    echo "   Please run with sudo: sudo ./start.sh"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs uploads

# Set proper permissions
chmod 755 logs uploads

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start the application
echo "🔨 Building and starting containers..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ PCAP Replaya is now running!"
    echo ""
    echo "🌐 Access the application at:"
    echo "   Frontend: http://localhost"
    echo "   Backend API: http://localhost:5000/api"
    echo ""
    echo "📊 To view logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 To stop the application:"
    echo "   docker-compose down"
else
    echo "❌ Failed to start services. Check logs with:"
    echo "   docker-compose logs"
    exit 1
fi
