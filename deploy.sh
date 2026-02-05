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
# We use --build to ensure the new Dockerfile changes are picked up
# We use -d to run in detached mode (background)
docker-compose down
docker-compose up --build -d

if [ $? -ne 0 ]; then
    echo "Error: Docker build/startup failed."
    exit 1
fi

echo "[3/3] Cleaning up unused images..."
docker image prune -f

echo "\nSUCCESS: Deployment complete!"
echo "API is running on port 8000."
echo "Collector is running in background."
