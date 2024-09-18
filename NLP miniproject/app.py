from flask import Flask, render_template, request, jsonify
import sqlite3
import re
import pyttsx3
from threading import Lock, Thread
from queue import Queue

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('reminders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pill_reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pill_name TEXT NOT NULL,
            reminder_time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Text-to-speech engine initialization
engine = pyttsx3.init()
speech_queue = Queue()
speech_lock = Lock()

def speak(text):
    with speech_lock:
        speech_queue.put(text)
        if not engine._inLoop:
            Thread(target=process_queue).start()

def process_queue():
    while not speech_queue.empty():
        text = speech_queue.get()
        engine.say(text)
        engine.runAndWait()

@app.route('/')
def home():
    return render_template('elderly-care-app.html')

@app.route('/pill_reminder')
def pill_reminder():
    return render_template('pill_reminders.html')

# Helper function to add pill reminder to the database
def add_pill_reminder(pill_name, reminder_time):
    conn = sqlite3.connect('reminders.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pill_reminders (pill_name, reminder_time) VALUES (?, ?)", (pill_name, reminder_time))
    conn.commit()
    conn.close()

# Helper function to retrieve all reminders
def get_all_reminders():
    conn = sqlite3.connect('reminders.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, pill_name, reminder_time FROM pill_reminders")
    reminders = cursor.fetchall()
    conn.close()
    return reminders

# Helper function to delete all reminders
def delete_all_reminders():
    conn = sqlite3.connect('reminders.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pill_reminders")
    conn.commit()
    conn.close()

# Helper function to delete specific reminder
def delete_reminder(pill_name, reminder_time):
    conn = sqlite3.connect('reminders.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pill_reminders WHERE pill_name = ? AND reminder_time = ?", (pill_name, reminder_time))
    conn.commit()
    conn.close()

# Voice command processing route
@app.route('/process_voice', methods=['POST'])
def process_voice():
    if request.is_json:
        data = request.get_json()
        command = data.get('command')
    else:
        return jsonify({"error": "Invalid request format"}), 400

    try:
        response_message = ""

        if 'set reminder for' in command:
            pill_name = re.search(r'set reminder for (.+?) at', command, re.IGNORECASE)
            reminder_time = re.search(r'at (\d{1,2}:\d{2} (?:AM|PM|a\.m\.|p\.m\.))', command, re.IGNORECASE)
            
            if pill_name and reminder_time:
                pill_name = pill_name.group(1).strip()
                reminder_time = reminder_time.group(1).strip()

                add_pill_reminder(pill_name, reminder_time)
                response_message = f"Reminder set to take {pill_name} at {reminder_time}"
                speak(response_message)

            else:
                response_message = "Could not extract pill name or time from your command."
                speak(response_message)

        elif 'show reminders' in command:
            reminders = get_all_reminders()
            if reminders:
                reminder_list = '\n'.join([f"{pill} at {time}" for id, pill, time in reminders])
                response_message = f"Your reminders are:\n{reminder_list}"
            else:
                response_message = "You have no reminders set."
                speak(response_message)

        elif 'weather' in command:
            response_message = "The weather today is sunny..."
            speak(response_message)

        elif 'delete reminder for' in command:
            pill_name = re.search(r'delete reminder for (.+?) at', command, re.IGNORECASE)
            reminder_time = re.search(r'at (\d{1,2}:\d{2} (?:AM|PM|a\.m\.|p\.m\.))', command, re.IGNORECASE)
            
            if pill_name and reminder_time:
                pill_name = pill_name.group(1).strip()
                reminder_time = reminder_time.group(1).strip()
                delete_reminder(pill_name, reminder_time)
                response_message = f"Reminder for {pill_name} at {reminder_time} has been deleted."
                speak(response_message)
            else:
                response_message = "Could not extract reminder details from your command."
                speak(response_message)

        elif 'delete all reminders' in command:
            delete_all_reminders()
            response_message = "All reminders have been deleted."
            speak(response_message)

        else:
            response_message = "Sorry, I didn't understand that."
            speak(response_message)

        # Print and speak the response message
        print(f"Response Message: {response_message}")  # Debugging line
        speak(response_message)
    
    except Exception as e:
        print(f"Error processing voice command: {e}")
        response_message = "An error occurred while processing your command."
        speak(response_message)

    return jsonify({"message": response_message})


# Helper function to add pill info to the timeline
@app.route('/add_pill_to_timeline', methods=['POST'])
def add_pill_to_timeline():
    if request.is_json:
        data = request.get_json()
        command = data.get('command')
        pill_info = command.replace('set reminder for ', '').replace(' at', '').strip()
        response_message = f"Added '{pill_info}' to timeline."
        # Assuming you handle this in JavaScript or the front-end code
        return jsonify({"message": response_message})
    else:
        return jsonify({"error": "Invalid request format"}), 400

if __name__ == '__main__':
    app.run(debug=True)
