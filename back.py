import cohere
import os
import json
from dotenv import load_dotenv
from textblob import TextBlob
import speech_recognition as sr
import pyttsx3

# Load environment variables
load_dotenv()

# Initialize Cohere client with API key
co = cohere.Client(os.getenv('COHERE_API_KEY'))

# Load conversation history from file (if exists)
def load_conversation_history():
    if os.path.exists("conversation_history.json"):
        with open("conversation_history.json", "r") as file:
            return json.load(file)
    return []

# Save conversation history to file
def save_conversation_history(conversation_history):
    with open("conversation_history.json", "w") as file:
        json.dump(conversation_history, file)

# Initialize conversation history
conversation_history = load_conversation_history()

# Analyze sentiment of the user input
def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity  # Returns a score between -1 and 1

# Function to get text response from Cohere based on user input
def get_text(input_text):
    # Analyze the sentiment of the user input
    sentiment_score = analyze_sentiment(input_text)
    if sentiment_score < -0.5:
        response_tone = "empathetic"
    elif sentiment_score > 0.5:
        response_tone = "excited"
    else:
        response_tone = "neutral"

    # Get only the last few messages of the conversation (to avoid excessive repetition)
    conversation_input = ""
    for entry in conversation_history[-2:]:  # Send only the last 2 exchanges
        conversation_input += f"{entry['sender']}: {entry['message']}\n"

    # Add the new user input to the conversation
    conversation_input += f"user: {input_text}\n"

    # Call Cohere API with context and sentiment-adjusted message
    try:
        output = co.chat(
            model='command-r-plus',
            message=f"The user seems {response_tone}. {conversation_input}"
        )
        response_text = output.text
    except Exception as e:
        response_text = "Oops! Something went wrong with the bot. Please try again."

    # Store user input and bot response in conversation history
    conversation_history.append({'sender': 'user', 'message': input_text})
    conversation_history.append({'sender': 'bot', 'message': response_text})

    # Save the updated conversation history
    save_conversation_history(conversation_history)

    return response_text

# Function to get voice input using speech recognition
def get_voice_input():
    recognizer = sr.Recognizer()  # Ensure recognizer is reinitialized each time
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)  # Set timeouts to avoid indefinite waiting
        try:
            input_text = recognizer.recognize_google(audio)
            print(f"User said: {input_text}")
            return input_text
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."
        except sr.RequestError:
            return "Sorry, there was an issue with the speech recognition service."
        except Exception as e:
            return f"An error occurred: {str(e)}"

# Function to speak the bot's response using TTS
def speak_text(output_text):
    try:
        # Reinitialize and use the TTS engine fresh each time
        tts_engine = pyttsx3.init()
        tts_engine.say(output_text)
        tts_engine.runAndWait()
        tts_engine.stop()  # Explicitly stop the engine after use
    except Exception as e:
        print(f"Error in speech synthesis: {e}")

# Summarize text using Cohere's summarization model
def summarize_text(input_text):
    summary = co.summarize(text=input_text)
    return summary.summary
