# Browser-Voice Docker Setup
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY proxy-requirements.txt .
COPY twilio/requirements.txt ./twilio/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r proxy-requirements.txt
RUN pip install --no-cache-dir -r twilio/requirements.txt

# Copy application code
COPY . .

# Create virtual environment for agent
RUN python -m venv /app/Vagent/venv
RUN /app/Vagent/venv/bin/pip install -r Vagent/requirements.txt

# Expose ports
EXPOSE 5000 5001 8081

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Browser-Voice services..."\n\
\n\
# Start proxy server in background\n\
python proxy-server.py &\n\
\n\
# Start Twilio webhook server in background\n\
cd twilio && python app.py &\n\
\n\
# Start WebSocket bridge in background\n\
cd twilio && python bridge.py &\n\
\n\
# Keep container running\n\
tail -f /dev/null\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Default command
CMD ["/app/start.sh"]
