from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import sqlite3
import re

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

# Voice command processing route
@app.route('/process_voice', methods=['POST'])
def process_voice():
    if request.is_json:
        data = request.get_json()
        command = data.get('command')
    else:
        return jsonify({"error": "Invalid request format"}), 400

    # NLP Logic for Processing Commands
    if 'set reminder' in command:
        # Extract pill name and reminder time from the voice command
        pill_name = re.search(r'set reminder to take (.+) at', command)
        reminder_time = re.search(r'at (\d{1,2}:\d{2} (?:AM|PM))', command)
        
        if pill_name and reminder_time:
            pill_name = pill_name.group(1).strip()
            reminder_time = reminder_time.group(1).strip()

            # Add reminder to the database
            add_pill_reminder(pill_name, reminder_time)
            response = {"message": f"Reminder set to take {pill_name} at {reminder_time}"}
        else:
            response = {"message": "Could not extract pill name or time from your command."}

    elif 'show reminders' in command:
        conn = sqlite3.connect('reminders.db')
        cursor = conn.cursor()
        cursor.execute("SELECT pill_name, reminder_time FROM pill_reminders")
        reminders = cursor.fetchall()
        conn.close()

        if reminders:
            reminder_list = '\n'.join([f"{pill} at {time}" for pill, time in reminders])
            response = {"message": f"Your reminders are:\n{reminder_list}"}
        else:
            response = {"message": "You have no reminders set."}

    elif 'weather' in command:
        response = {"message": "The weather today is sunny..."}

    else:
        response = {"message": "Sorry, I didn't understand that."}
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)


'''
Set reminder:

"Set reminder to take aspirin at 7:00 PM"
"Set reminder to take paracetamol at 9:30 AM"

Show reminders:

"Show my pill reminders"
'''
