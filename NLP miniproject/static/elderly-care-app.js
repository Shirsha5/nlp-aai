// Add event listeners to the 'speak-btn'
document.getElementById('speak-btn').addEventListener('click', function() {
    captureVoiceCommand();
});

document.getElementById('speak-btn').addEventListener('click', function() {
    console.log("Button clicked!");
    activateVoiceCommand();
});

// Function to capture the voice command using speech recognition
function captureVoiceCommand() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    
    recognition.lang = 'en-US'; // Set the language of the speech recognition
    recognition.interimResults = false; // Disable interim results
    
    recognition.onstart = function() {
        console.log("Voice recognition started. Try speaking into the microphone.");
    };

    recognition.onspeechend = function() {
        recognition.stop();
    };

    recognition.onresult = function(event) {
        const command = event.results[0][0].transcript;
        console.log("Voice command received: " + command);

        // Send the command to the backend
        sendVoiceCommandToBackend(command);
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
    };

    // Start speech recognition
    recognition.start();
}

// Function to send the recognized voice command to the Flask backend
function sendVoiceCommandToBackend(command) {
    fetch('/process_voice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command: command })
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response from the backend
        console.log(data.message);
        document.getElementById('assistant-output').textContent = data.message;
        
        // If the command includes adding a reminder, update the UI with the pill info
        if (data.message.includes("Reminder set")) {
            addPillToTimeline(command); // Custom function to add reminder visually
        }
    })
    .catch(error => console.error('Error sending voice command:', error));
}

// Function to visually add the pill reminder to the timeline
function addPillToTimeline(command) {
    const pillInfo = command.replace('set reminder to', '').trim(); // Extract the pill info from command

    const timelineContainer = document.getElementById('timelineContainer');

    const timelineItem = document.createElement('div');
    timelineItem.className = 'timeline-item';

    timelineItem.innerHTML = `
        <div class="pill-time">TBD</div>
        <div>${pillInfo}</div>
        <div class="status">Active</div>
    `;

    timelineContainer.appendChild(timelineItem);
}
