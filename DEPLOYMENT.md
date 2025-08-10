# Browser-Voice Deployment Guide

This guide covers different deployment options for the Browser-Voice project.

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.8+
- Git
- API keys for LiveKit, Cartesia, and OpenAI

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/vamsikris7000/Browser-voice.git
   cd browser-voice
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   # or
   ./quick-start.sh
   ```

3. **Update environment variables**
   Edit the `.env` file with your API keys:
   ```bash
   # LiveKit Configuration
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   
   # AI Service APIs
   CARTESIA_API_KEY=your_cartesia_api_key
   CHATBOT_API_URL=https://api.openai.com/v1/chat/completions
   CHATBOT_API_KEY=your_openai_api_key
   ```

4. **Start the services**
   ```bash
   # Terminal 1: Proxy server
   python proxy-server.py
   
   # Terminal 2: AI Agent
   cd Vagent
   source venv/bin/activate
   livekit-agents start-agent --url "wss://your-project.livekit.cloud" --token "YOUR_TOKEN" --room "voice-chat-room" --entrypoint-fnc "agent:entrypoint" --prewarm-fnc "agent:prewarm"
   
   # Terminal 3: Twilio webhook (optional)
   cd twilio
   python app.py
   
   # Terminal 4: WebSocket bridge (optional)
   cd twilio
   python bridge.py
   ```

5. **Access the application**
   - Open `public/index.html` in your browser
   - Or serve with a local web server: `python -m http.server 8000`

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - Web interface: http://localhost
   - Proxy server: http://localhost:5001
   - Twilio webhook: http://localhost:5000

### Using Docker directly

1. **Build the image**
   ```bash
   docker build -t browser-voice .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name browser-voice \
     -p 5000:5000 \
     -p 5001:5001 \
     -p 8081:8081 \
     --env-file .env \
     browser-voice
   ```

## ☁️ Cloud Deployment

### Heroku

1. **Create a Heroku app**
   ```bash
   heroku create your-browser-voice-app
   ```

2. **Set environment variables**
   ```bash
   heroku config:set LIVEKIT_URL=wss://your-project.livekit.cloud
   heroku config:set LIVEKIT_API_KEY=your_livekit_api_key
   heroku config:set LIVEKIT_API_SECRET=your_livekit_api_secret
   heroku config:set CARTESIA_API_KEY=your_cartesia_api_key
   heroku config:set CHATBOT_API_KEY=your_openai_api_key
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

### AWS EC2

1. **Launch an EC2 instance**
   - Use Ubuntu 20.04 or later
   - Configure security groups to allow ports 80, 443, 5000, 5001, 8081

2. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git nginx
   ```

3. **Clone and setup**
   ```bash
   git clone https://github.com/vamsikris7000/Browser-voice.git
   cd browser-voice
   python3 setup.py
   ```

4. **Configure nginx**
   ```bash
   sudo cp nginx.conf /etc/nginx/nginx.conf
   sudo systemctl restart nginx
   ```

5. **Run with systemd**
   Create service files for each component and run as system services.

### Google Cloud Run

1. **Build and push to Container Registry**
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT/browser-voice
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy browser-voice \
     --image gcr.io/YOUR_PROJECT/browser-voice \
     --platform managed \
     --allow-unauthenticated \
     --port 5001
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LIVEKIT_URL` | LiveKit server URL | Yes |
| `LIVEKIT_API_KEY` | LiveKit API key | Yes |
| `LIVEKIT_API_SECRET` | LiveKit API secret | Yes |
| `CARTESIA_API_KEY` | Cartesia TTS API key | Yes |
| `CHATBOT_API_URL` | OpenAI API endpoint | Yes |
| `CHATBOT_API_KEY` | OpenAI API key | Yes |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | No |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | No |

### Port Configuration

| Port | Service | Description |
|------|---------|-------------|
| 5000 | Twilio Webhook | Handles incoming phone calls |
| 5001 | Proxy Server | CORS proxy for token generation |
| 8081 | WebSocket Bridge | Audio bridge for phone calls |
| 80 | Nginx | Web interface (Docker only) |

## 🔒 Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **HTTPS**: Use HTTPS in production for all endpoints
3. **CORS**: Configure CORS properly for your domain
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Firewall**: Configure firewall rules appropriately

## 📊 Monitoring

### Health Checks

- Proxy server: `GET /health`
- Twilio webhook: `GET /health`
- Docker: Built-in health checks

### Logs

- Application logs: Check console output
- Docker logs: `docker logs browser-voice`
- Nginx logs: `/var/log/nginx/`

### Metrics

Consider adding monitoring with:
- Prometheus + Grafana
- AWS CloudWatch
- Google Cloud Monitoring

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports are not in use by other services
2. **API key errors**: Verify all API keys are correct and have proper permissions
3. **CORS errors**: Check browser console and proxy configuration
4. **Audio issues**: Verify microphone permissions and browser compatibility

### Debug Mode

Enable debug logging by setting:
```bash
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
```

### Support

For issues and questions:
- Check the main README.md
- Review the troubleshooting section
- Create an issue in the GitHub repository
