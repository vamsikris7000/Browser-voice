# Browser-Voice

A comprehensive voice AI assistant system that enables real-time voice conversations through web browsers and phone calls. This project integrates LiveKit for real-time communication, Twilio for phone call support, and various AI plugins for speech processing.

## 🚀 Features

- **Web Browser Voice Chat**: Real-time voice conversations through web browsers
- **Phone Call Integration**: AI assistant accessible via phone calls using Twilio
- **Advanced Speech Processing**: 
  - Deepgram for Speech-to-Text
  - Cartesia for Text-to-Speech
  - Silero for Voice Activity Detection
  - Noise cancellation for better audio quality
- **Multi-modal Support**: Handles both browser and phone call scenarios
- **Real-time Streaming**: Low-latency audio streaming with LiveKit

## 📁 Project Structure

```
browser-voice/
├── Vagent/                    # Main AI Agent
│   ├── agent.py              # Core agent implementation
│   ├── requirements.txt      # Python dependencies
│   └── README.md            # Agent-specific documentation
├── twilio/                   # Phone call integration
│   ├── app.py               # Twilio webhook server
│   ├── bridge.py            # WebSocket bridge for audio
│   └── requirements.txt     # Twilio dependencies
├── public/                   # Web client
│   ├── index.html           # Main web interface
│   ├── browser-client.js    # Browser client logic
│   └── test-token.html      # Token testing page
├── proxy-server.py          # CORS proxy for token generation
├── proxy-requirements.txt   # Proxy server dependencies
└── README.md               # This file
```

## 🛠️ Prerequisites

- Python 3.8+
- Node.js (optional, for development)
- LiveKit account and credentials
- Twilio account (for phone calls)
- Deepgram API key
- Cartesia API key
- OpenAI API key (for chatbot)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vamsikris7000/Browser-voice.git
cd browser-voice
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# AI Service APIs
CARTESIA_API_KEY=your_cartesia_api_key
CHATBOT_API_URL=https://api.openai.com/v1/chat/completions
CHATBOT_API_KEY=your_openai_api_key

# Twilio Configuration (for phone calls)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

### 3. Install Dependencies

#### For the AI Agent:
```bash
cd Vagent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### For the Proxy Server:
```bash
pip install -r proxy-requirements.txt
```

#### For Twilio Components:
```bash
cd twilio
pip install -r requirements.txt
```

## 🚀 Running the Application

### Option 1: Web Browser Voice Chat

1. **Start the Proxy Server** (for token generation):
```bash
python proxy-server.py
```

2. **Start the AI Agent**:
```bash
cd Vagent
source venv/bin/activate
livekit-agents start-agent \
  --url "wss://your-project.livekit.cloud" \
  --token "YOUR_AGENT_TOKEN" \
  --room "voice-chat-room" \
  --entrypoint-fnc "agent:entrypoint" \
  --prewarm-fnc "agent:prewarm"
```

3. **Open the Web Interface**:
   - Navigate to `public/index.html` in your browser
   - Click "Start Call" to begin voice conversation

### Option 2: Phone Call Integration

1. **Start the Twilio Webhook Server**:
```bash
cd twilio
python app.py
```

2. **Start the WebSocket Bridge**:
```bash
cd twilio
python bridge.py
```

3. **Start the AI Agent** (same as above)

4. **Configure Twilio**:
   - Set your Twilio phone number's webhook URL to: `http://your-server:5000/twilio-stream`
   - Configure ngrok or similar for public access

## 🔑 Generating LiveKit Tokens

The system uses a proxy server to generate LiveKit tokens. The proxy forwards requests to an AWS endpoint:

```bash
# Token generation endpoint
POST http://localhost:5001/proxy/tokens/generate?agent_name=agent-1
```

## 📞 Phone Call Flow

1. User calls Twilio number
2. Twilio webhook receives call and connects to WebSocket bridge
3. Bridge connects to LiveKit room with phone-specific settings
4. AI agent joins the room and processes audio
5. Real-time conversation between user and AI

## 🌐 Web Browser Flow

1. User opens web interface
2. Browser requests LiveKit token via proxy
3. Browser connects to LiveKit room
4. AI agent joins and conversation begins
5. Real-time audio streaming between browser and AI

## 🔧 Configuration

### Agent Configuration

The AI agent automatically detects whether it's handling a phone call or browser session and adjusts settings accordingly:

- **Phone Calls**: Slower speech rate, enhanced noise cancellation
- **Browser Sessions**: Standard settings for optimal web experience

### Audio Settings

- **Sample Rate**: 16kHz for optimal quality
- **Channels**: Mono for phone calls, Stereo for browser
- **Noise Cancellation**: Enabled for both modes
- **Voice Activity Detection**: Silero VAD for efficient processing

## 🐛 Troubleshooting

### Common Issues

1. **Token Generation Fails**:
   - Check proxy server is running on port 5001
   - Verify API keys in environment variables

2. **Audio Not Working**:
   - Ensure microphone permissions are granted
   - Check browser console for errors
   - Verify LiveKit connection

3. **Phone Calls Not Connecting**:
   - Check Twilio webhook configuration
   - Verify bridge server is running
   - Check ngrok tunnel if using

### Logs

- Agent logs: Check console output for detailed agent activity
- Browser logs: Open browser developer tools
- Twilio logs: Check Flask server console output

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LiveKit for real-time communication infrastructure
- Twilio for phone call integration
- Deepgram for speech-to-text capabilities
- Cartesia for text-to-speech synthesis
- Silero for voice activity detection

## 📞 Support

For support and questions:
- Create an issue in this repository
- Check the documentation in each component's README
- Review the troubleshooting section above 
