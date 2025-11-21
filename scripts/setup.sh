#!/bin/bash

echo "🚀 Setting up AI Constitutional Framework Development Environment"

# Check prerequisites
if ! command -v python &> /dev/null; then
    echo "❌ Python is required but not installed."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed."
    exit 1
fi

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Setup database
echo "🗄️ Initializing database..."
make db-reset

# Run tests
echo "🧪 Running test suite..."
make test

# Start development services
echo "🐳 Starting development stack..."
make docker-up

echo "✅ Setup complete!"
echo "📚 Documentation: http://localhost:8001"
echo "🔌 API Server: http://localhost:8000"
echo "🗄️ Database: localhost:5432"
