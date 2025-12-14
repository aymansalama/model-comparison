#!/bin/bash

# NLP Benchmark Platform Setup Script

set -e

echo "========================================"
echo "NLP Benchmark Platform Setup"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "IMPORTANT: Please edit .env and add your API keys:"
    echo "  - OPENAI_API_KEY (for OpenAI models)"
    echo "  - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY (for Bedrock models)"
    echo ""
else
    echo "✓ .env file already exists"
fi

# Create storage directories
echo "Creating storage directories..."
mkdir -p backend/storage/{uploads,custom_tasks,results,datasets}
echo "✓ Created storage directories"
echo ""

# Build and start services
echo "Building and starting services..."
docker compose up -d --build

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Services are starting up. This may take a minute..."
echo ""
echo "Access the platform at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker compose logs -f"
echo ""
echo "To stop services:"
echo "  docker compose down"
echo ""
