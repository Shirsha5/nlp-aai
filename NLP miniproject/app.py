from flask import Flask, render_template, request, jsonify
import sqlite3
import re
import pyttsx3
from threading import Lock, Thread
from queue import Queue
import vonage
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import os
import pytz

client = vonage.Client(key="4a6b3b47", secret="CCrFDJrdWOat7jhG")
sms = vonage.Sms(client)

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

# Initialize APScheduler
scheduler = BackgroundScheduler()

def check_reminders():
    conn = sqlite3.connect('reminders.db')
    cursor = conn.cursor()
    cursor.execute("SELECT pill_name, reminder_time FROM pill_reminders")
    reminders = cursor.fetchall()
    
    # Get current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist).strftime("%I:%M %p")
        
    for pill_name, reminder_time in reminders:
        print(reminder_time)
        if reminder_time == current_time:
            print(f"Reminder: Time to take {pill_name}!")  
            speak(f"Reminder: Time to take {pill_name}!")

    conn.close()

# Add a job to the scheduler
scheduler.add_job(check_reminders, 'interval', minutes=1)  # Check every minute
scheduler.start()

# Text-to-speech engine initialization
engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[0].id) #male
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
        
        
@app.route('/community-updates')
def community_updates():
    return render_template('community-updates.html')

@app.route('/')
def home():
    return render_template('elderly-care-app.html')

@app.route('/pill-reminder')
def pill_reminder():
    return render_template('pill-reminders.html')

# Helper function to add pill reminder to the database
def add_pill_reminder(pill_name, reminder_time):
    # Remove periods and ensure AM/PM is in uppercase
    reminder_time = reminder_time.replace(".", "").strip().upper()  # e.g., "11:04 P.M." -> "11:04 PM"
    
    # Ensure it's in a consistent format
    conn = sqlite3.connect('reminders.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pill_reminders (pill_name, reminder_time) VALUES (?, ?)", (pill_name, reminder_time))
    conn.commit()
    conn.close()
    
    '''
#-------------------------- TEST
def manual_add_reminder(pill_name, reminder_time):
    # Call the add_pill_reminder function to insert directly
    add_pill_reminder(pill_name, reminder_time)

# Example usage
manual_add_reminder("Aspirin", "11:04 PM")
manual_add_reminder("Vitamin D", "08:30 AM")
'''


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
    
import requests

def get_weather(city):
    print(f"Fetching weather for: {city}")
    # Your API key should be a string
    API_KEY = 'ad371e891249d722045f73b35fb610f9'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    response = requests.get(url)
    print(f"API response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Received data: {data}")
        weather_description = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"The weather in {city} is currently {weather_description} with a temperature of {temp}°C."
    else:
        return "Sorry, I couldn't fetch the weather information."


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

        if 'set reminder' in command or 'set a reminder' in command or 'set alarm' in command:
            pill_name = re.search(r'set reminder for (.+?) at', command, re.IGNORECASE)
            reminder_time = re.search(r'at (\d{1,2}:\d{2} (?:AM|PM|a\.m\.|p\.m\.))', command, re.IGNORECASE)
            
            if pill_name and reminder_time:
                pill_name = pill_name.group(1).strip()
                reminder_time = reminder_time.group(1).strip().upper()  # Convert to uppercase

                # Add the pill reminder
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
            
        elif 'open community updates' in command:
            response_message = "Opening community updates page."
            speak(response_message)
            return jsonify({"redirect": "/community-updates"})
    
        elif 'open pill reminders' in command:
            response_message = "Opening pill reminders page."
            speak(response_message)
            return jsonify({"redirect": "/pill-reminders"})
        
            
        elif "explorer" in command:
            os.system("explorer")
        elif "Notepad" in command:
            os.system("notepad")
        elif "chrome" in command:
            os.system("start chrome")
        elif "microsoft" in command:
            os.system("start microsoft-edge:")
        elif "calculator" in command:
            os.system("calc")
            
        elif "goodbye" in command:
            response_message = "Goodbye! Have a great day!"
            speak(response_message)
            
        elif "hello" in command:
            response_message = "Hello! How can i assist you?"
            speak(response_message)
            
        elif "SOS" in command:
            responseData = sms.send_message(
                {
                    "from": "Elderly Care App SOS Team",

                    "to": "919004128510",
                    "text": "SOSOSOS Help im under the water",   # DONT FORGET TO CHANGE    
                }
            )
            
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                response_message = "Message sent successfully."
                speak(response_message)
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
                response_message = "Message failed"
                speak(response_message)
                
                
                
        elif "weather" in command:
        # Extract the city name from the command
            if "in" in command:
                city = command.split("in")[-1].strip()
                weather_info = get_weather(city)
                print(weather_info)
                response_message = weather_info
                speak(response_message)
                
            else:
                print("Please specify a city for the weather information.")
    

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
    app.run(debug=True, port= 5001)
