#!/bin/bash
# এই ফাইলটি scripts/ ডিরেক্টরিতে তৈরি করুন

echo "🚀 Deploying ZombieCoder Unified Agent System..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv zombiecoder_env
source zombiecoder_env/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install flask requests psutil pyyaml

# Create directories
echo "📁 Creating directory structure..."
mkdir -p memory data/memory logs extensions

# Check Ollama
echo "🔍 Checking Ollama..."
if ! curl -s http://127.0.0.1:8155/api/tags > /dev/null; then
    echo "⚠️  Ollama not running on port 8155. Please start Ollama first."
    echo "💡 Run: ollama serve --port 8155"
fi

# Start the agent
echo "🤖 Starting ZombieCoder Agent..."
python unified_agent_system.py &

echo "✅ Deployment completed!"
echo "🌐 Agent running on: http://localhost:8001"
echo "📊 Check status: curl http://localhost:8001/status"
echo "💬 Test chat: curl -X POST http://localhost:8001/chat -H 'Content-Type: application/json' -d '{\"message\":\"Hello\"}'"