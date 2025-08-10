#!/bin/bash

# Browser-Voice Quick Start Script
# This script helps you get the project running quickly

set -e  # Exit on any error

echo "🚀 Browser-Voice Quick Start"
echo "============================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating one from template..."
    cat > .env << EOF
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# AI Service APIs
CARTESIA_API_KEY=your_cartesia_api_key
CHATBOT_API_URL=https://api.openai.com/v1/chat/completions
CHATBOT_API_KEY=your_openai_api_key

# Twilio Configuration (for phone calls)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
EOF
    echo "✅ Created .env file. Please update it with your API keys before continuing."
    echo "   Edit the .env file and run this script again."
    exit 0
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt
pip3 install -r proxy-requirements.txt

# Set up virtual environment for agent
if [ ! -d "Vagent/venv" ]; then
    echo "🐍 Setting up virtual environment..."
    cd Vagent
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 To start the application:"
echo ""
echo "1. Start the proxy server (in one terminal):"
echo "   python3 proxy-server.py"
echo ""
echo "2. Start the AI agent (in another terminal):"
echo "   cd Vagent"
echo "   source venv/bin/activate"
echo "   livekit-agents start-agent --url 'wss://your-project.livekit.cloud' --token 'YOUR_TOKEN' --room 'voice-chat-room' --entrypoint-fnc 'agent:entrypoint' --prewarm-fnc 'agent:prewarm'"
echo ""
echo "3. Open public/index.html in your browser"
echo ""
echo "📖 For detailed instructions, see README.md"
echo ""
echo "🎉 Happy coding!"
