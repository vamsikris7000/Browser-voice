# Voice-Enabled AI Assistant

This project implements a voice-enabled AI assistant using LiveKit, which provides real-time voice interaction capabilities. The assistant can listen to user input, process it through a chatbot API, and respond with natural-sounding speech.

## Features

- Real-time voice interaction
- Speech-to-Text conversion using Deepgram
- Text-to-Speech synthesis using Cartesia
- Voice Activity Detection (VAD)
- Background noise cancellation
- Streaming responses from chatbot API
- Conversation tracking and management

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- API keys for:
  - Cartesia (for TTS)
  - Deepgram (for STT)
  - Chatbot API

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:
```env
CARTESIA_API_KEY=your_cartesia_api_key
CHATBOT_API_URL=your_chatbot_api_url
CHATBOT_API_KEY=your_chatbot_api_key
```

## Project Structure

```
.
├── agent.py              # Main agent implementation
├── requirements.txt      # Project dependencies
├── .env                 # Environment variables (create this)
└── README.md           # This documentation
```

## Code Overview

### Main Components

1. **CustomChatbotAgent Class**
   - Handles voice interactions
   - Manages conversation state
   - Processes user input and generates responses

2. **Voice Processing**
   - Speech-to-Text (STT) using Deepgram
   - Text-to-Speech (TTS) using Cartesia
   - Voice Activity Detection (VAD)
   - Noise cancellation

3. **API Integration**
   - External chatbot API integration
   - Streaming response handling
   - Conversation tracking

## Running the Application

1. Ensure all environment variables are set in `.env`

2. Run the application:
```bash
python agent.py
```

3. The agent will:
   - Connect to LiveKit room
   - Initialize voice processing
   - Send an initial greeting
   - Begin listening for user input

## Usage

1. When the application starts, it will send an initial greeting
2. Speak clearly into your microphone
3. The agent will:
   - Convert your speech to text
   - Process it through the chatbot API
   - Respond with synthesized speech

## Troubleshooting

1. **No Audio Input**
   - Check microphone permissions
   - Verify audio input device selection
   - Ensure VAD is working correctly

2. **API Connection Issues**
   - Verify API keys in `.env`
   - Check internet connection
   - Ensure API endpoints are accessible

3. **Voice Processing Problems**
   - Check Deepgram and Cartesia API status
   - Verify audio quality and background noise
   - Ensure proper microphone setup

## Development Notes

- The code uses asynchronous programming (async/await) for better performance
- Error handling is implemented throughout the codebase
- Logging is configured for debugging purposes
- The agent maintains conversation context using conversation IDs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Support

For support, please [add contact information or support channels] 
