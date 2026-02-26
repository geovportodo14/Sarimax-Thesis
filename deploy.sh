#!/bin/bash

echo "========================================"
echo "   SARIMAX THESIS - AUTO DEPLOYMENT"
echo "========================================"

echo "[1/3] Pulling latest changes from GitHub..."
git pull
if [ $? -ne 0 ]; then
    echo "Error: Git pull failed. Please check your connection or conflicts."
    exit 1
fi

echo "[2/3] Rebuilding Docker Containers..."

# Detect which docker compose command is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

$COMPOSE_CMD down
$COMPOSE_CMD up --build -d

if [ $? -ne 0 ]; then
    echo "Error: Docker build/startup failed."
    exit 1
fi

echo "[3/3] Cleaning up unused images..."
docker image prune -f

echo "\nSUCCESS: Deployment complete!"
echo "SARIMAX API (Predictions/Alerts): http://localhost:8000"
echo "Dashboard API (History/Trends):   http://localhost:5000"
echo "Data Collector: Running in background"
