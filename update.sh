#!/bin/bash

# PCAP Replaya Update Script
# This script updates an existing PCAP Replaya deployment to the latest version

set -e

echo "🔄 PCAP Replaya Update Script"
echo "============================="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script requires root privileges for Docker operations."
    echo "   Please run with sudo: sudo $0"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed or not in PATH."
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ No docker-compose.yml found in current directory."
    echo "   Please run this script from your PCAP Replaya deployment directory."
    exit 1
fi

# Detect which registry is being used
REGISTRY_TYPE=""
if grep -q "ghcr.io" docker-compose.yml; then
    REGISTRY_TYPE="GitHub Container Registry"
elif grep -q "blinkzero" docker-compose.yml; then
    REGISTRY_TYPE="Docker Hub"
else
    echo "❌ Unable to detect registry type from docker-compose.yml"
    exit 1
fi

echo "📦 Detected registry: $REGISTRY_TYPE"
echo ""

# Show current running containers
echo "📊 Current deployment status:"
docker-compose ps
echo ""

# Ask for confirmation
read -p "🔄 Do you want to update to the latest version? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Update cancelled."
    exit 0
fi

echo "⏳ Updating PCAP Replaya..."

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose pull

# Stop current containers
echo "🛑 Stopping current containers..."
docker-compose down

# Start with new images
echo "🚀 Starting updated containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ PCAP Replaya has been successfully updated!"
    echo ""
    echo "📊 Updated deployment status:"
    docker-compose ps
    echo ""
    echo "🌐 Access the application at:"
    echo "   http://localhost"
    echo "   http://$(hostname -I | awk '{print $1}')"
    echo ""
    echo "📋 View logs: docker-compose logs -f"
else
    echo "❌ Update failed. Check logs with: docker-compose logs"
    exit 1
fi
