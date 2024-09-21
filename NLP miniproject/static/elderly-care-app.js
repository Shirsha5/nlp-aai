// Voice command handling
document.getElementById('speak-btn').addEventListener('click', () => {
    captureVoiceCommand();
});

function captureVoiceCommand() {
    if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
        alert('Speech Recognition API is not supported in this browser.');
        return;
    }
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    
    recognition.lang = 'en-US'; // Set the language of the speech recognition
    recognition.interimResults = false; // Disable interim results
    
    recognition.onstart = function() {
        console.log("Voice recognition started. Try speaking into the microphone.");
        speak("Please speak into the microphone.");
    };

    recognition.onspeechend = function() {
        console.log("Speech ended.");
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
        if (event.error === 'no-speech') {
            console.log("No speech detected. Please try again.");
        } else if (event.error === 'audio-capture') {
            console.log("Audio capture failed. Check your microphone.");
        } else if (event.error === 'not-allowed') {
            console.log("Permission to use microphone was denied.");
        }
    };

    // Start speech recognition
    recognition.start();
}

function sendVoiceCommandToBackend(command) {
    fetch('/process_voice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command: command })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Handle the response from the backend
        console.log(data.message);
        document.getElementById('assistant-output').textContent = data.message;
        
        // Redirect if specified
        if (data.redirect) {
            window.location.href = data.redirect; // Redirect to the specified page
        }

        if (data.message.includes("Reminder set")) {
            addPillToTimeline(command); // Custom function to add reminder visually
        }
    })
    .catch(error => console.error('Error sending voice command:', error));
}

let voices = [];

function populateVoiceList() {
    voices = window.speechSynthesis.getVoices();
}

window.speechSynthesis.onvoiceschanged = populateVoiceList;

function speak(message) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(message);
        
        // Wait until voices are loaded
        if (voices.length === 0) {
            console.error('No voices available.');
            return;
        }

        // Attempt to select a specific male voice
        const maleVoice = voices.find(voice => voice.name.includes('Male')) || voices.find(voice => voice.default);
        utterance.voice = maleVoice;

        utterance.onstart = function() {
            console.log("Speaking: " + message);
        };

        utterance.onerror = function(event) {
            console.error("SpeechSynthesisUtterance error: ", event);
        };

        window.speechSynthesis.speak(utterance);
    } else {
        alert('Speech Synthesis API is not supported in this browser.');
    }
}

function addPillToTimeline(command) {
    const pillInfo = command.replace('set reminder to take ', '').replace(' at', '').trim(); // Extract the pill info from command

    const reminderBox = document.getElementById('reminder-box');
    const reminderList = document.getElementById('reminders-list');

    reminderList.textContent = reminderList.textContent === 'No reminders set.' ? pillInfo : reminderList.textContent + ', ' + pillInfo;
}
