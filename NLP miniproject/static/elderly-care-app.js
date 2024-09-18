<script>
    document.getElementById('speak-btn').addEventListener('click', () => {
        captureVoiceCommand();
    });

    function captureVoiceCommand() {
        if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
            alert('Speech Recognition API is not supported in this browser.');
            return;
        }

        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = function() {
            console.log("Voice recognition started. Please speak into the microphone.");
            speakMessage("Voice recognition started. Please speak into the microphone.");
            document.getElementById('assistant-output').textContent = "Listening...";
        };

        recognition.onspeechend = function() {
            console.log("Speech ended.");
            speakMessage("Speech ended.");
            recognition.stop();
        };

        recognition.onresult = function(event) {
            const command = event.results[0][0].transcript;
            console.log("Voice command received: " + command);
            speakMessage("Voice command received: " + command);
            sendVoiceCommandToBackend(command);
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            speakMessage(`Error: ${event.error}`);
            document.getElementById('assistant-output').textContent = `Error: ${event.error}`;
        };

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
            const message = data.message;
            console.log(message);
            speakMessage(message); // Speak the response message
            document.getElementById('assistant-output').textContent = message;
            
            if (message.includes("Reminder set")) {
                addPillToTimeline(command); // Custom function to add reminder visually
            }
        })
        .catch(error => {
            console.error('Error sending voice command:', error);
            speakMessage(`Error: ${error.message}`);
            document.getElementById('assistant-output').textContent = `Error: ${error.message}`;
        });
    }

    function speakMessage(message) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(message);
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
        const pillInfo = command.replace('set reminder for ', '').replace(' at', '').trim();
        const reminderBox = document.getElementById('reminder-box');
        const reminderList = document.getElementById('reminders-list');
        reminderList.textContent = reminderList.textContent === 'No reminders set.' ? pillInfo : reminderList.textContent + ', ' + pillInfo;
    }
</script>
