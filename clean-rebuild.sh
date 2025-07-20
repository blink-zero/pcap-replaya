#!/bin/bash

# Clean Docker Cache and Rebuild Script for Linux/Mac

set -e

echo "🧹 Cleaning Docker cache and rebuilding PCAP Replaya..."

echo "🛑 Stopping all containers..."
docker-compose down

echo "🗑️ Removing existing containers and images..."
docker-compose down --rmi all --volumes --remove-orphans

echo "🧽 Pruning Docker system (this will remove all unused containers, networks, images)..."
docker system prune -af

echo "🔄 Pruning Docker volumes..."
docker volume prune -f

echo "🔄 Pruning Docker networks..."
docker network prune -f

echo "📦 Removing any dangling images..."
docker image prune -af

echo "🔨 Building and starting fresh containers..."
docker-compose up --build --force-recreate

echo "✅ Clean rebuild complete!"
