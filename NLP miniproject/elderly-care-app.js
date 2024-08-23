document.getElementById('speak-btn').addEventListener('click', function() {
  captureVoiceCommand();
});

function captureVoiceCommand() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.start();

  recognition.onresult = function(event) {
      const command = event.results[0][0].transcript;
      console.log('Voice command received: ' + command);
      processVoiceCommand(command);
  };

  recognition.onerror = function(event) {
      console.error('Error occurred in recognition: ' + event.error);
  };
}

function processVoiceCommand(command) {
  if (command.includes('set reminder')) {
      const reminder = command.replace('set reminder to', '').trim();
      setReminder(reminder);
  } else if (command.includes('show reminders')) {
      showReminders();
  } else if (command.includes('weather')) {
      getWeather(); // Example function you'd implement
  } else {
      document.getElementById('assistant-output').textContent = "Sorry, I didn't understand that.";
  }
}

function setReminder(reminder) {
  const list = document.getElementById('reminders-list');
  const listItem = document.createElement('div');
  listItem.textContent = reminder;
  listItem.classList.add('reminder-item');
  list.appendChild(listItem);
  speak("Reminder set for " + reminder);
}

function showReminders() {
  const reminders = Array.from(document.getElementsByClassName('reminder-item')).map(item => item.textContent).join(', ');
  if (reminders) {
      speak("You have the following reminders: " + reminders);
  } else {
      speak("You have no reminders set.");
  }
}

function speak(text) {
  const synth = window.speechSynthesis;
  const utterThis = new SpeechSynthesisUtterance(text);
  synth.speak(utterThis);
}
