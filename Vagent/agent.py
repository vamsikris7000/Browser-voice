from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext, ChatMessage, StopResponse
from livekit.plugins import (
    deepgram,
    cartesia,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
import aiohttp
import os
import json
import logging
import asyncio
import signal
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")
CHATBOT_API_URL = os.getenv("CHATBOT_API_URL")
CHATBOT_API_KEY = os.getenv("CHATBOT_API_KEY")

if not CARTESIA_API_KEY:
    raise ValueError("CARTESIA_API_KEY is required")

def strip_markdown(text):
    # Remove common markdown formatting for clearer TTS
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`', '', text)
    text = re.sub(r'#+ ', '', text)
    text = re.sub(r'- ', '', text)
    return text

def shutdown_handler(signum, frame):
    logger.info("Received shutdown signal. Exiting gracefully...")
    asyncio.get_event_loop().stop()

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

class CustomChatbotAgent(Agent):
    def __init__(self):
        super().__init__(instructions="You are a helpful voice AI assistant for phone calls. Keep responses concise and conversational.")
        self._livekit_session = None
        self._session = None
        self.last_transcript = ""
        self.conversation_id = ""
        self.is_phone_call = False

    async def initialize(self):
        if self._session is None:
            connector = aiohttp.TCPConnector(force_close=True)
            self._session = aiohttp.ClientSession(connector=connector)

    async def cleanup(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def generate_reply(self, transcript: str, **kwargs) -> str:
        if not self._session:
            await self.initialize()

        headers = {
            "Authorization": f"Bearer {CHATBOT_API_KEY}",
            "Content-Type": "application/json"
        }

        # Modify the prompt for phone calls to be more concise
        query = transcript
        if self.is_phone_call:
            query = f"[Phone Call Mode - Keep response under 30 words] {transcript}"

        payload = {
            "inputs": {},
            "query": query,
            "response_mode": "streaming",
            "conversation_id": self.conversation_id,
            "user": "phone-user" if self.is_phone_call else "abc-123",
            "files": []
        }

        try:
            logger.info(f"Sending to chatbot API: {transcript}")
            async with self._session.post(CHATBOT_API_URL, headers=headers, json=payload) as response:
                response_text = await response.text()
                if response.status != 200:
                    logger.error(f"Chatbot API error: {response.status} {response_text}")
                    return "Sorry, I couldn't process your request."

                reply = ""
                for line in response_text.splitlines():
                    if line.startswith("data:"):
                        try:
                            event = json.loads(line[len("data:"):].strip())
                            if "conversation_id" in event and not self.conversation_id:
                                self.conversation_id = event["conversation_id"]
                                logger.info(f"New conversation ID: {self.conversation_id}")
                            if 'answer' in event:
                                reply += event['answer']
                        except Exception as e:
                            logger.error(f"JSON parse error: {line} — {e}")

                return reply or "Sorry, I couldn't process your request."

        except Exception as e:
            logger.error(f"generate_reply error: {e}")
            return "Sorry, I couldn't process your request."

    # async def on_user_turn(self, session: AgentSession, turn):
    #     transcript = getattr(turn, 'transcript', '').strip()
    #     if transcript and transcript != self.last_transcript:
    #         logger.info(f"💬 New user transcript (Phone: {self.is_phone_call}): {transcript}")
    #         self.last_transcript = transcript
    #         reply = await self.generate_reply(transcript)
    #         if reply:
    #             logger.info(f"🔣️ Saying reply: {reply}")
    #             clean_reply = strip_markdown(reply)
    #             # For phone calls, speak slower and clearer
    #             await session.say(clean_reply, allow_interruptions=True)

    async def on_user_turn_completed(
        self, turn_ctx: ChatContext, new_message: ChatMessage,
    ) -> None:
        transcript = new_message.text_content
        logger.info(f"on_user_turn_completed: transcript: {transcript}")

        reply = await self.generate_reply(transcript)
        await self.speak_reply(reply)
        raise StopResponse()

    async def speak_reply(self, reply):
        if reply and self._livekit_session:
            clean_reply = strip_markdown(reply)
            await self._livekit_session.say(clean_reply, allow_interruptions=True)
            logger.info("Replied to user with TTS (from speak_reply)")

def prewarm(proc: agents.JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: agents.JobContext):
    logger.info("Connecting to LiveKit room...")
    await ctx.connect()
    logger.info(f"Connected to room: {ctx.room.name}")

    # Check if this is a phone call by room name or participant identity
    room_name = ctx.room.name or ""
    is_phone_call = room_name.startswith("phone-call-") or any(
        p.identity.startswith("phone-") for p in ctx.room.remote_participants.values()
    )

    agent = CustomChatbotAgent()
    agent.is_phone_call = is_phone_call
    await agent.initialize()
    
    # Configure TTS settings based on call type
    tts_config = {
        "model": "sonic-english",
        "voice": "bf0a246a-8642-498a-9950-80c35e9276b5",
        "api_key": CARTESIA_API_KEY,
    }
    
    if is_phone_call:
        # Slower speed and clearer pronunciation for phone calls
        tts_config["speed"] = 0.7
        logger.info("🎤 Configured for phone call mode")
    else:
        tts_config["speed"] = 0.8

    # Fixed STT configuration - removed 'vad_events' parameter
    stt_config = {
        "model": "nova-3", 
        "language": "multi",
        "punctuate": True,
    }
    
    # Add phone-specific settings if available
    if is_phone_call:
        # You can add other valid parameters here if needed
        logger.info("🎤 Using phone-optimized STT settings")

    session = AgentSession(
        stt=deepgram.STT(**stt_config),
        llm=None,
        tts=cartesia.TTS(**tts_config),
        vad=ctx.proc.userdata["vad"],
    )
    agent._livekit_session = session
    
    # Configure room input options for phone calls
    room_input_options = RoomInputOptions()
    if is_phone_call:
        # More aggressive noise cancellation for phone audio
        room_input_options.noise_cancellation = noise_cancellation.BVC()
        # FIXED: Removed the problematic auto_subscribe line
        pass
    else:
        room_input_options.noise_cancellation = noise_cancellation.BVC()

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=room_input_options,
    )

    logger.info("Agent session started successfully")
    
    # Initial greeting
    if is_phone_call:
        greeting = await agent.generate_reply("Say a brief greeting for a phone call, under 20 words")
    else:
        greeting = await agent.generate_reply("Greet the user and offer your assistance.")
    
    if greeting:
        clean_greeting = strip_markdown(greeting)
        logger.info(f"📢 Initial greeting: {clean_greeting}")
        await session.say(clean_greeting, allow_interruptions=True)

    try:
        # The agent will run until the job is cancelled
        await asyncio.sleep(3600) # Keep the agent alive
    except asyncio.CancelledError:
        logger.info("Agent job cancelled.")
    except Exception as e:
        logger.error(f"Agent session error: {e}")
    finally:
        await agent.cleanup()
        logger.info("Cleaned up session")

if __name__ == "__main__":
    # To run this agent, you need to use the livekit-agents CLI.
    # 1. Make sure you have your .env file with the required API keys.
    # 2. Generate a LiveKit token with an identity that includes 'agent' (e.g., 'my-test-agent')
    #    and grants to join the room 'my-agent-room'.
    # 3. Run the following command in your terminal:
    #
    # livekit-agents start-agent \
    #   --url "wss://vijay-cc7nu555.livekit.cloud" \
    #   --token "YOUR_AGENT_LIVEKIT_TOKEN" \
    #   --room "my-agent-room" \
    #   --entrypoint-fnc "agent:entrypoint" \
    #   --prewarm-fnc "agent:prewarm"

    # Note: The 'agent:entrypoint' and 'agent:prewarm' refer to the functions
    # in this file (agent.py).
    
    # This part is for direct execution if needed, but CLI is recommended.
    # It requires environment variables for LIVEKIT_URL, LIVEKIT_API_KEY, etc.
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm)
    )