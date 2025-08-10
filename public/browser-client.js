const {
    Room,
    RoomEvent,
    RemoteParticipant,
    RemoteTrack,
    RemoteTrackPublication,
    Participant,
    LocalAudioTrack,
} = LivekitClient;

// --- UI Elements ---
const startButton = document.getElementById('start-button');
const endButton = document.getElementById('end-button');
const statusDiv = document.getElementById('status');

// --- LiveKit Connection Details ---
// IMPORTANT: Replace with your LiveKit server URL.
// You can get this from your LiveKit Cloud project dashboard.
// Example: wss://my-project.livekit.cloud
const livekitUrl = 'wss://agent-364qtybd.livekit.cloud';

// --- Application State ---
let room;
let isConnected = false;
let localAudioTrack = null;

// --- Main Functions ---

async function fetchLivekitToken(agentName = 'agent-1') {
    const endpoint = `http://localhost:5001/proxy/tokens/generate?agent_name=${agentName}`;
    
    console.log('Fetching token from local proxy:', endpoint);
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Response error:', errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('Token data received:', data);
        
        return {
            token: data.token,
            livekitUrl: data.livekit_url,
            roomName: data.room_name
        };
    } catch (error) {
        console.error('Fetch error details:', error);
        throw new Error(`Token fetch failed: ${error.message}`);
    }
}

/**
 * Connects to the LiveKit room and sets up listeners.
 */
async function startCall() {
    if (isConnected) return;

    statusDiv.textContent = 'Requesting token...';
    startButton.disabled = true;
    endButton.disabled = true;

    let token, livekitUrl, roomName;
    try {
        const tokenData = await fetchLivekitToken('agent-1');
        token = tokenData.token;
        livekitUrl = tokenData.livekitUrl;
        roomName = tokenData.roomName;
    } catch (error) {
        console.error('Failed to fetch token:', error);
        statusDiv.textContent = `Token error: ${error.message}`;
        startButton.disabled = false;
        endButton.disabled = true;
        return;
    }

    // Create a new room instance
    room = new Room({
        audioCaptureDefaults: {
            autoGainControl: true,
            noiseSuppression: true,
        },
    });

    statusDiv.textContent = 'Connecting...';

    try {
        // Connect to the room
        await room.connect(livekitUrl, token);
        isConnected = true;

        // Update UI
        statusDiv.textContent = 'Connected. Waiting for AI agent...';
        startButton.disabled = true;
        endButton.disabled = false;

        // Publish user's microphone audio
        await publishMicrophone();

        // Set up room event listeners
        room.on(RoomEvent.TrackSubscribed, handleTrackSubscribed);
        room.on(RoomEvent.Disconnected, handleDisconnect);
        room.on(RoomEvent.ParticipantConnected, (participant) => {
            console.log(`Participant connected: ${participant.identity}`);
            if (participant.identity.includes('agent')) {
                statusDiv.textContent = 'AI Agent has joined the call.';
            }
        });

    } catch (error) {
        console.error('Failed to connect to LiveKit room:', error);
        statusDiv.textContent = `Error: ${error.message}`;
        isConnected = false;
        startButton.disabled = false;
        endButton.disabled = true;
    }
}

/**
 * Publishes the user's microphone to the room.
 */
async function publishMicrophone() {
    try {
        localAudioTrack = await LivekitClient.createLocalAudioTrack();
        await room.localParticipant.publishTrack(localAudioTrack);
        console.log('Microphone published successfully.');
    } catch (error) {
        console.error('Failed to publish microphone:', error);
        statusDiv.textContent = 'Could not get microphone access.';
    }
}

/**
 * Handles incoming tracks from remote participants (the AI agent).
 * @param {RemoteTrack} track
 * @param {RemoteTrackPublication} publication
 * @param {RemoteParticipant} participant
 */
function handleTrackSubscribed(track, publication, participant) {
    console.log(`Track subscribed: ${track.sid} from ${participant.identity}`);
    
    // Check if the track is an audio track from an agent
    if (track.kind === 'audio') {
        statusDiv.textContent = 'AI is speaking...';
        const audioElement = track.attach();
        audioElement.setAttribute('data-agent-audio', 'true');
        document.body.appendChild(audioElement); // Play the audio

        // You can add logic here to know when the AI stops speaking
        // for example, by monitoring the audio level.
        // For simplicity, we'll just let it play.
    }
}

/**
 * Disconnects from the LiveKit room and cleans up.
 */
function endCall() {
    if (!isConnected || !room) return;

    statusDiv.textContent = 'Disconnecting...';
    room.disconnect();
}

/**
 * Handles the disconnection event.
 */
function handleDisconnect() {
    console.log('Disconnected from the room.');
    isConnected = false;
    localAudioTrack = null;

    // Clean up UI
    statusDiv.textContent = 'Call ended. Ready to connect.';
    startButton.disabled = false;
    endButton.disabled = true;
    
    // Remove any attached agent audio elements
    const audioElements = document.querySelectorAll('audio[data-agent-audio]');
    audioElements.forEach(el => el.remove());
}

// --- Event Listeners ---
startButton.addEventListener('click', startCall);
endButton.addEventListener('click', endCall); 