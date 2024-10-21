# -*- coding: utf-8 -*-
"""
**INTGRATING** **OPENFDA API**

**CHATBOT WITH FUZZY MATCHING OF FAQS, LOGGING CONVERSATION HISTORY, FETCHING DRUG DATA FROM OPENFDA AND SUMMARIZING IT INCLUDED**

"""

import requests  # for dealing with the API calls
import torch
from transformers import BlenderbotForConditionalGeneration, BlenderbotTokenizer, pipeline
from fuzzywuzzy import fuzz  # for fuzzy matching

api_key = "EdOLHO85EdgL29kyULi3HCbmblyxvSq926w01Ga6"


summarizer = pipeline("summarization")


model_name = "facebook/blenderbot-400M-distill"


tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)

faq_data = {
    "what is this app about": "This app is designed to help elderly with pill management, emergency help, setting reminders and appointment management. It is an all-in-one app that simplifies healthcare management for the elderly. With simple voice commands, the user can navigate through the application. The dynamic dashboard also provides information about the user's appointments, reminders, medications, weather information and more!",
    "how do i create an account": "Simply registering your mobile number will create your account. Once you have created an account, you can feed in your medications, reminders and appointments. And don't forget to add your emergency contacts!",
    "how do i set a new reminder": "Simply say your voice command out loud and the job will be done! For example, you can say something like: Set reminder for 10 AM tomorrow.",
    "if i need help, then how do i contact my loved ones": "Saying an emergency key word will trigger the SOS system and send a message to your emergency contacts immediately.",
    "what if i feel lonely": "Your virtual companion will be available to have a conversation with you any time!",
    "what are the emergency contacts for?": "The emergency contacts help us know whom to contact in case you need urgent help. This can be your loved ones, doctor, or a friend. A SOS message is prepared and sent to your emergency contacts if you need urgent help or are in an emergency situation.",
    "what if i feel sick": "You can trigger the emergency SOS through a voice command and your emergency contacts as well as doctor will be informed immediately.",
    "how to set a new pill/medication": "Simply through voice commands, you can set up a new pill reminder. Once logged into our database, we will make sure to inform you on time to take it.",
    "how to set up a new appointment": "Simply through voice commands, you can set up a new upcoming appointment with your doctor. For example, you can say something like: Set an appointment for 2 PM today.",
    "what if i forget about my appointment?": "The virtual assistant will remind you of your upcoming appointments and the dashboard will also give you an overview.",
    "what if i forget to take my pills/medications?": "The virtual assistant will remind you beforehand to take your medication and the reminders will not stop until a confirmation is received.",
    "how to use this app": "This application is completely voice-controlled and specially designed to be super user-friendly. It is an all-in-one app that simplifies healthcare management for the elderly. You can navigate through the app simply through voice commands, setting new reminders, appointments or for talking to your virtual companion. All you need to do is feed in your voice command! Let me know if you have any more questions about this app!",
}

def get_drug_info(api_key, drug_name):
    url = f"https://api.fda.gov/drug/label.json?api_key={api_key}&search={drug_name}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            result = data['results'][0]
            description = result.get('description', 'No description available.')
            indications = result.get('indications_and_usage', ['No indications available.'])
            warnings = result.get('warnings', ['No warnings available.'])

            # Combine the information into a coherent paragraph
            indications_str = ", ".join(indications)
            warnings_str = ", ".join(warnings)
            full_info = (f"{drug_name.capitalize()} is a popular medication. Here’s what I know about it: "
                         f"{indications_str}. Description: {description}. "
                         f"Important warnings include: {warnings_str}.")
            return full_info
        else:
            return "No information found for this drug."
    else:
        return f"Error fetching data from openFDA: {response.status_code} - {response.text}"

def summarize_info(full_info):

    introductory_line = full_info.split(": ", 1)[0]


    summary_text = full_info.split(": ", 1)[1]


    if len(summary_text) > 1024:
        summary_text = summary_text[:1024]

    summary = summarizer(summary_text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']


    return f"{introductory_line}: {summary}"

def check_faq(user_input):
    best_match = None
    highest_score = 0
    for question, answer in faq_data.items():
        score = fuzz.partial_ratio(user_input.lower(), question)
        if score > highest_score:
            highest_score = score
            best_match = answer

    if highest_score >= 70:
        return best_match
    return None

conversation_history = ""
def generate_response(user_input):
    global conversation_history


    if "drug" in user_input.lower() or "medicine" in user_input.lower():
        words = user_input.split()
        if "drug" in words:
            drug_index = words.index("drug") + 1
        elif "medicine" in words:
            drug_index = words.index("medicine") + 1

        if drug_index < len(words):
            drug_name = words[drug_index]
            drug_info = get_drug_info(api_key, drug_name)

            if isinstance(drug_info, str):

                summarized_info = summarize_info(drug_info)
                return summarized_info
            else:
                return drug_info

    # Fuzzy matching for FAQs
    faq_response = check_faq(user_input)
    if faq_response:
        return faq_response

    # Add user input to conversation history
    conversation_history += f"User: {user_input}\n"
    inputs = tokenizer.encode("conversation: " + conversation_history, return_tensors="pt")
    outputs = model.generate(inputs, max_length=150, num_beams=5, early_stopping=True)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    conversation_history += f"Chatbot: {response}\n"

    return response
