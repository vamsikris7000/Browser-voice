from flask import Flask, request, Response
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlaskServer")

# Replace this with your bridge WebSocket ngrok URL
BRIDGE_WEBSOCKET_URL = "wss://live.xpectrum-ai.com/bridge"
# ttps://04f6-2405-201-c02d-68e0-f959-a882-f137-5b6b.ngrok-free.app
@app.route("/twilio-stream", methods=["POST"])
def twilio_stream():
    caller = request.form.get('From', 'Unknown')
    logger.info(f"📞 Incoming call from {caller}")
    
    # Improved TwiML with better audio settings
    twiml = f"""<?xml version='1.0' encoding='UTF-8'?>
<Response>
  <Say voice="alice" rate="medium">Hello! Connecting you to your AI assistant. Please wait a moment.</Say>
  <Pause length="1"/>
  <Connect>
    <Stream url="{BRIDGE_WEBSOCKET_URL}">
      <Parameter name="callSid" value="{request.form.get('CallSid', '')}" />
      <Parameter name="from" value="{caller}" />
    </Stream>
  </Connect>
</Response>"""
    
    logger.info(f"📋 Sending TwiML response for call {request.form.get('CallSid', 'unknown')}")
    return Response(twiml, mimetype="text/xml")

@app.route("/call-status", methods=["POST"])
def call_status():
    """Handle call status updates from Twilio"""
    call_status = request.form.get('CallStatus')
    call_sid = request.form.get('CallSid')
    logger.info(f"📊 Call {call_sid} status: {call_status}")
    return Response("OK", mimetype="text/plain")

@app.route("/")
def index():
    return "✅ Flask + Twilio Webhook is running."

@app.route("/health")
def health():
    return {"status": "healthy", "service": "twilio-webhook"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
