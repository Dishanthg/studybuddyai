import os
import sys
import time
import openai
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from colorama import init, Fore, Style
import pytesseract
from PIL import Image
import tkinter as tk
from tkinter import filedialog

# ========== Setup ==========

# Load environment variables
load_dotenv()

# OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
openai.api_key = api_key

# Setup Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Setup TTS
engine = pyttsx3.init()

# Init colorama
init(autoreset=True)

# Setup Tkinter (hide root window)
root = tk.Tk()
root.withdraw()

# ========== Helper Functions ==========

def typing_animation(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def listen_for_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(Fore.YELLOW + "Listening for your question... (Press 'Ctrl + C' to cancel)")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print(Fore.CYAN + "Processing...")
        question = recognizer.recognize_google(audio)
        print(Fore.GREEN + f"You said: {question}")
        return question
    except sr.UnknownValueError:
        print(Fore.RED + "Sorry, I couldn't understand that.")
        return None
    except sr.RequestError:
        print(Fore.RED + "Speech recognition service error.")
        return None

# ========== OpenAI Chat Function ==========

def ask_openai(prompt):
    try:
        client = openai.OpenAI()  # Uses the default api_key
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, an error occurred: {str(e)}"

# ========== Main Loop ==========

print(Fore.CYAN + "Hello! I am your AI Study Bot (OpenAI Version). Ask me anything! (Type 'exit' to quit)\n")

while True:
    mode = input(Fore.YELLOW + "Choose input method (mic/image/type/exit): ").strip().lower()

    if mode == "mic":
        question = listen_for_speech()
        if question:
            print(Fore.YELLOW + "Bot is thinking...", end="\r")
            time.sleep(1)
            response = ask_openai(question)
            print(Fore.GREEN + "Bot: ", end="")
            typing_animation(response)
            engine.say(response)
            engine.runAndWait()

    elif mode == "image":
        print("\n🔹 Please select an image.")
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
        )
        if not file_path:
            print("No file selected.")
            continue

        try:
            img = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(img).strip()
            print("\n📝 Extracted Text:\n" + "-"*35)
            print(extracted_text)
        except Exception as e:
            print(f"Image error: {e}")
            continue

        try:
            prompt = f"Answer based on this text:\n\n{extracted_text}"
            response = ask_openai(prompt)
            print("\n🤖 OpenAI Answer:\n" + "-"*35)
            typing_animation(response)
            engine.say(response)
            engine.runAndWait()
        except Exception as e:
            print(f"OpenAI error: {e}")

    elif mode == "type":
        user_input = input(Fore.BLUE + "You: " + Style.RESET_ALL)
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print(Fore.MAGENTA + "Bot: ", end="")
            typing_animation("Goodbye! Happy studying! 🚀")
            engine.say("Goodbye! Happy studying!")
            engine.runAndWait()
            break

        print(Fore.YELLOW + "Bot is thinking...", end="\r")
        time.sleep(1)
        response = ask_openai(user_input)
        print(Fore.GREEN + "Bot: ", end="")
        typing_animation(response)
        engine.say(response)
        engine.runAndWait()

    elif mode == "exit":
        print(Fore.MAGENTA + "Bot: ", end="")
        typing_animation("Goodbye! Happy studying! 🚀")
        engine.say("Goodbye! Happy studying!")
        engine.runAndWait()
        break

    else:
        print(Fore.RED + "Invalid option. Choose 'mic', 'image', 'type', or 'exit'.")
