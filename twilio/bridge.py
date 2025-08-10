import asyncio
import websockets
import json
import base64
import logging
import uuid
import numpy as np
from livekit import rtc, api
import warnings

# Suppress the audioop deprecation warning
warnings.filterwarnings("ignore", category=DeprecationWarning, module="audioop")
import audioop

# Set logging to INFO to reduce debug spam
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WebSocketBridge")

LIVEKIT_URL = "wss://vijay-cc7nu555.livekit.cloud"
BRIDGE_WEBSOCKET_PORT = 8081

LIVEKIT_API_KEY = "APIepVPtV8w5B5k"
LIVEKIT_API_SECRET = "XQWtCYZkFh1ejDzIPL8pfx5gqwtRpfGmwhVfw67TshdC"

class TwilioLiveKitBridge:
    def __init__(self):
        self.room = None
        self.audio_source = None
        self.connected = False
        self.websocket = None
        self.call_sid = None
        self.room_name = None
        self.stream_sid = None
        self.websocket_connected = False
        self.audio_frame_count = 0
        
    def generate_token(self, room_name, participant_identity):
        """Generate a LiveKit token for the specific room and participant"""
        try:
            token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
                .with_identity(participant_identity) \
                .with_name(f"Phone Call {participant_identity}") \
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                ))
            return token.to_jwt()
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDk0OTgwOTIsImlzcyI6IkFQSWVwVlB0Vjh3NUI1ayIsIm5iZiI6MTc0OTM5ODA5Miwic3ViIjoidmlqYXkiLCJ2aWRlbyI6eyJjYW5QdWJsaXNoIjp0cnVlLCJjYW5QdWJsaXNoRGF0YSI6dHJ1ZSwiY2FuU3Vic2NyaWJlIjp0cnVlLCJyb29tIjoidm9pY2UiLCJyb29tSm9pbiI6dHJ1ZX19.A7cBmcM7SR4KXc7eurFqo_SHUyz_b61WTs0QrgJ_npE"

    async def connect_to_livekit(self, call_sid):
        try:
            self.call_sid = call_sid
            self.room_name = f"phone-call-{call_sid[:8]}"
            
            logger.info(f"Connecting to LiveKit room: {self.room_name}")
            
            token = self.generate_token(self.room_name, f"phone-{call_sid[:8]}")
            self.room = rtc.Room()
            
            @self.room.on("track_subscribed")
            def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
                logger.info(f"Agent audio track subscribed from {participant.identity}")
                if track.kind == rtc.TrackKind.KIND_AUDIO:
                    asyncio.create_task(self.handle_agent_audio(track))

            @self.room.on("participant_connected")
            def on_participant_connected(participant: rtc.RemoteParticipant):
                logger.info(f"Participant connected: {participant.identity}")

            await self.room.connect(LIVEKIT_URL, token)
            logger.info(f"Connected to LiveKit room: {self.room_name}")

            # Create audio source with optimal settings for phone calls
            self.audio_source = rtc.AudioSource(sample_rate=16000, num_channels=1)
            audio_track = rtc.LocalAudioTrack.create_audio_track("microphone", self.audio_source)
            
            options = rtc.TrackPublishOptions()
            options.source = rtc.TrackSource.SOURCE_MICROPHONE
            await self.room.local_participant.publish_track(audio_track, options)

            # Shorter wait time to reduce latency
            await asyncio.sleep(1.0)
            
            self.connected = True
            logger.info("LiveKit connected and ready for audio")
            
        except Exception as e:
            logger.error(f"LiveKit connection error: {e}")
            self.connected = False

    async def handle_agent_audio(self, track: rtc.AudioTrack):
        """Handle audio from the agent and send it to Twilio with minimal latency"""
        try:
            logger.info("Starting agent audio capture")
            audio_stream = rtc.AudioStream(track)
            
            async for frame_event in audio_stream:
                if not hasattr(frame_event, 'frame'):
                    continue
                
                frame = frame_event.frame
                
                if self.websocket and self.websocket_connected:
                    try:
                        audio_data = self.convert_to_twilio_format(frame)
                        if audio_data:
                            message = {
                                "event": "media",
                                "streamSid": self.stream_sid,
                                "media": {
                                    "payload": audio_data
                                }
                            }
                            await self.websocket.send(json.dumps(message))
                            
                            # Log every 100 frames to reduce spam
                            self.audio_frame_count += 1
                            if self.audio_frame_count % 100 == 0:
                                logger.info(f"Sent {self.audio_frame_count} audio frames to Twilio")
                                
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("WebSocket connection closed")
                        break
                    except Exception as send_error:
                        logger.error(f"Failed to send audio to Twilio: {send_error}")
                        continue
                else:
                    # Shorter sleep to reduce latency
                    await asyncio.sleep(0.05)
                    if not self.websocket_connected:
                        logger.warning("WebSocket not connected, stopping audio capture")
                        break
                        
        except Exception as e:
            logger.error(f"Error handling agent audio: {e}")

    def convert_to_twilio_format(self, frame: rtc.AudioFrame):
        """Optimized audio conversion with minimal processing"""
        try:
            pcm_data = None
            
            # Fast path: Try direct data extraction first
            if hasattr(frame, 'data'):
                if isinstance(frame.data, (bytes, bytearray)):
                    pcm_data = bytes(frame.data)
                elif hasattr(frame.data, 'tobytes'):
                    pcm_data = frame.data.tobytes()
                elif isinstance(frame.data, np.ndarray):
                    pcm_data = frame.data.tobytes()
                else:
                    # Fallback conversion
                    try:
                        pcm_data = np.array(frame.data, dtype=np.int16).tobytes()
                    except:
                        pass
            
            if pcm_data is None:
                return None
            
            # Get frame properties with defaults
            sample_rate = getattr(frame, 'sample_rate', 16000)
            num_channels = getattr(frame, 'num_channels', 1)
            
            # Optimize: Only convert sample rate if needed
            if sample_rate != 8000:
                try:
                    pcm_data = audioop.ratecv(pcm_data, 2, num_channels, sample_rate, 8000, None)[0]
                except audioop.error:
                    return None
            
            # Optimize: Only convert to mono if stereo
            if num_channels == 2:
                pcm_data = audioop.tomono(pcm_data, 2, 1, 1)
            
            # Convert PCM to μ-law and encode to base64 in one go
            try:
                ulaw_data = audioop.lin2ulaw(pcm_data, 2)
                return base64.b64encode(ulaw_data).decode('utf-8')
            except audioop.error:
                return None
            
        except Exception:
            # Silent fail to avoid log spam
            return None

    async def process_incoming_audio(self, audio_data):
        """Optimized incoming audio processing"""
        if not self.connected or not self.audio_source:
            return
            
        try:
            # Fast audio processing pipeline
            decoded = base64.b64decode(audio_data)
            pcm_audio = audioop.ulaw2lin(decoded, 2)
            pcm_16k = audioop.ratecv(pcm_audio, 2, 1, 8000, 16000, None)[0]
            audio_array = np.frombuffer(pcm_16k, dtype=np.int16)
            
            frame = rtc.AudioFrame(
                data=audio_array,
                sample_rate=16000,
                num_channels=1,
                samples_per_channel=len(audio_array)
            )
            
            await self.audio_source.capture_frame(frame)
            
        except Exception:
            # Silent fail to avoid log spam during normal operation
            pass

    async def websocket_handler(self, websocket):
        logger.info("Twilio WebSocket connection established")
        self.websocket = websocket
        self.websocket_connected = True
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    continue

                event = data.get("event")
                
                if event == "connected":
                    logger.info("Twilio stream connected")
                    
                elif event == "start":
                    start_data = data.get("start", {})
                    self.call_sid = start_data.get("callSid", f"call-{uuid.uuid4().hex[:8]}")
                    self.stream_sid = start_data.get("streamSid")
                    logger.info(f"Call started: {self.call_sid}")
                    
                    if not self.connected:
                        await self.connect_to_livekit(self.call_sid)
                        
                elif event == "media":
                    payload = data.get("media", {}).get("payload")
                    if payload and self.connected:
                        await self.process_incoming_audio(payload)
                        
                elif event == "stop":
                    logger.info("Stream stopped by Twilio")
                    break
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            self.websocket_connected = False
            if self.room and self.connected:
                await self.room.disconnect()
            self.connected = False
            self.websocket = None
            logger.info("Disconnected from LiveKit")

async def start_server():
    async def handle_connection(websocket):
        logger.info(f"New connection from {websocket.remote_address}")
        bridge = TwilioLiveKitBridge()
        await bridge.websocket_handler(websocket)
    
    try:
        server = await websockets.serve(handle_connection, "0.0.0.0", BRIDGE_WEBSOCKET_PORT)
        logger.info(f"WebSocket server ready at ws://0.0.0.0:{BRIDGE_WEBSOCKET_PORT}")
        
        await server.wait_closed()
        
    except Exception as e:
        logger.error(f"Server startup error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped")
