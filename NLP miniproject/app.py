#test app.py

from flask import Flask, render_template, request, jsonify, send_from_directory, session
from chatbot import generate_response
import sqlite3
import re
import pyttsx3
from threading import Lock, Thread, Event
from queue import Queue
import vonage
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import os
import pytz
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

import pygame
import subprocess


 
app = Flask(__name__) 

def speak_no(text):
    tts = gTTS(text=text, lang='en')
    audio_file = f"output_{int(time.time())}.mp3"  # Unique filename
    tts.save(audio_file)
    subprocess.Popen(["start", "/min", "wmplayer", audio_file], shell=True)
    #os.system(f"start /min {audio_file}")
    
def speak(text):
    engine = pyttsx3.init()  # Initialize the TTS engine
    engine.say(text)  # Queue the text to be spoken
    engine.runAndWait()

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/static/<filename>')
def images(filename):
    return send_from_directory('static', filename)


'''
# Text-to-speech engine initialization
engine = pyttsx3.init()
speech_queue = Queue()
speech_lock = Lock()

# Helper functions for text-to-speech (TTS)
def process_queue():
    while not speech_queue.empty():
        text = speech_queue.get()
        engine.say(text)
        try:
            engine.runAndWait()
        except Exception as e:
            print(f"Error in TTS engine: {e}")
            engine.endLoop()  # End any stuck loops
            engine.startLoop(False)  # Restart the loop

def speak(text):
    with speech_lock:
        speech_queue.put(text)
        if not engine._inLoop:
            # Safely start the process_queue in a thread
            Thread(target=process_queue).start()

def reinitialize_engine():
    global engine
    engine.endLoop()  # End any existing loop
    engine = pyttsx3.init()  # Reinitialize the engine
'''

''' new
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
        '''
'''

@app.route('/community-updates')
def community_updates():
    return render_template('community-updates.html')
    '''
@app.route('/elderly-care-app')
def application():
    return render_template('elderly-care-app.html')

@app.route('/pill-reminder')
def pill_reminder():
    return render_template('pill-reminders.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/learn-more')
def learn_more():
    return render_template('learn-more.html')

client = vonage.Client(key="4a6b3b47", secret="CCrFDJrdWOat7jhG")
sms = vonage.Sms(client)


'''@app.route('/')
def home():
    return render_template('elderly-care-app.html')
'''
# Database initialization
def init_db():
    with sqlite3.connect('pillpal.db') as conn:  
        cursor = conn.cursor()
        # User table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        # Pills table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pill_name TEXT NOT NULL,
                dosage TEXT,
                frequency INTEGER NOT NULL,
                time_to_take TEXT NOT NULL,
                next_restocking_date TEXT
            )
        ''')
        # Pill reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pill_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pill_id INTEGER NOT NULL,
                pill_name TEXT NOT NULL,
                reminder_date TEXT NOT NULL,
                reminder_time TEXT NOT NULL,
                FOREIGN KEY (pill_name) REFERENCES pills (pill_name),
                FOREIGN KEY (pill_id) REFERENCES pills (id)
            )
        ''')
        # Community updates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS community_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                update_text TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

init_db()

# User authentication helpers
def signup_user(username, password, email):
    with sqlite3.connect('pillpal.db') as conn:  
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))
        conn.commit()

def login_user(username, password):
    with sqlite3.connect('pillpal.db') as conn:  
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        return user
    
# Initialize APScheduler
scheduler = BackgroundScheduler()

# Pill reminder control events
pill_taken_event = Event()  # Will be set when the user says "pill taken"

# Function to repeat reminder every 5 minutes if "pill taken" is not said
def check_reminders():
    conn = sqlite3.connect('pillpal.db')
    cursor = conn.cursor()
    cursor.execute("SELECT pill_name, reminder_time FROM pill_reminders")
    reminders = cursor.fetchall()

    # Get current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist).strftime("%I:%M %p")

    for pill_name, reminder_time in reminders:
        
        if reminder_time == current_time:
            print(f"Reminder: Time to take {pill_name}!")
            speak(f"Reminder: Time to take {pill_name}!")

            # Set event to wait for the keyword
            pill_taken_event.clear()

            # Start a thread to keep reminding every 5 minutes until "pill taken" is heard
            Thread(target=wait_for_pill_taken, args=(pill_name,)).start()

    conn.close()

def wait_for_pill_taken(pill_name):
    # Keep reminding every 5 minutes until "pill taken" is detected
    while not pill_taken_event.wait(timeout=300):  # Wait for 5 minutes
        print(f"Reminder: Please take {pill_name}!")
        speak(f"Reminder: Please take {pill_name}!")
        
# Add a job to the scheduler
scheduler.add_job(check_reminders, 'interval', minutes=1)  # Check every minute
scheduler.start()


# NLP techniques for date parsing
def parse_nlp_date(date_str):
    parsed_date = dateparser.parse(date_str)
    if parsed_date:
        return parsed_date.strftime('%Y-%m-%d')
    return None

# Community updates
def add_community_update(update_text):
    with sqlite3.connect('pillpal.db') as conn: 
        cursor = conn.cursor()
        cursor.execute("INSERT INTO community_updates (update_text) VALUES (?)", (update_text,))
        conn.commit()

def get_community_updates():
    with sqlite3.connect('pillpal.db') as conn:  
        cursor = conn.cursor()
        cursor.execute("SELECT update_text FROM community_updates ORDER BY created_at DESC")
        updates = cursor.fetchall()
        return updates

# Routes for login and signup
from flask import session, redirect, render_template

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        signup_user(username, password, email)
        session['success'] = "Signup successful!"  # Set a session variable
        home()
        return redirect('/elder-care-app')  # Redirect to the login page
    return render_template('signup.html', error=None, success=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = login_user(username, password)
        if user:
            session['success'] = "Login successful!"  # Set a session variable
            home()
            return redirect('/elder-care-app')  # Redirect to the app page
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html', error=None)

# Community updates page
@app.route('/community-updates')
def community_updates():
    updates = get_community_updates()
    return render_template('community_updates.html', updates=updates)


# Helper function to add pill reminder to the database
def add_pill_reminder(pill_name, reminder_time):
    # Remove periods and ensure AM/PM is in uppercase
    reminder_time = reminder_time.replace(".", "").strip().upper()  # e.g., "11:04 P.M." -> "11:04 PM"
    
    # Ensure it's in a consistent format
    conn = sqlite3.connect('pillpal.db')
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
    conn = sqlite3.connect('pillpal.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, pill_name, reminder_time FROM pill_reminders")
    reminders = cursor.fetchall()
    conn.close()
    return reminders

# Helper function to delete all reminders
def delete_all_reminders():
    conn = sqlite3.connect('pillpal.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pill_reminders")
    conn.commit()
    conn.close()

# Helper function to delete specific reminder
def delete_reminder(pill_name, reminder_time):
    conn = sqlite3.connect('pillpal.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pill_reminders WHERE pill_name = ? AND reminder_time = ?", (pill_name, reminder_time))
    conn.commit()
    conn.close()
    
import requests

def get_weather(city):
    print(f"Fetching weather for: {city}")
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
                speak(response_message)

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

                    "to": "918668655668",
                    "text": "ALERT FROM PILLPAL! YOUR LOVED ONE NEEDS IMMEDIATE ATTENTION!!",   # DONT FORGET TO CHANGE    
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

        elif 'chat' in command or 'talk to chatbot' in command:
            # Call the chatbot function to get the response
            response_message = generate_response(command)
            speak(response_message)
                    
        # Detect if user says "pill taken"
        elif 'pill taken' in command.lower():
            pill_taken_event.set()  # Stop reminders
            response_message = "Great! You've taken your pill."
            speak(response_message)

        else:
            response_message = "Sorry, I didn't understand that."
            speak(response_message)

        # Print and speak the response message
        print(f"Response Message: {response_message}")  # Debugging line
      #  speak(response_message)
    
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
        # handled this in js
        return jsonify({"message": response_message})
    else:
        return jsonify({"error": "Invalid request format"}), 400

if __name__ == '__main__':
    app.run(debug=True, port= 5001)

