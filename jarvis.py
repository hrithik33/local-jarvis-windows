import os
import sys
import subprocess
import datetime
import webbrowser

import ollama
import speech_recognition as sr
import pyttsx3


# ============================================================
# J.A.R.V.I.S. v0.3
# Local AI PC Assistant
# ============================================================

MODEL = "qwen3:4b"

# Your working microphone
MIC_ID = 1


# ============================================================
# JARVIS PERSONALITY
# ============================================================

SYSTEM_PROMPT = """
You are JARVIS, a personal AI assistant running locally on a Windows PC.

Personality:
- Calm
- Intelligent
- Professional
- Friendly
- Slightly futuristic
- Helpful
- Concise

Always identify yourself as JARVIS.
Never say that you are Qwen.

You are connected to a Windows PC.

IMPORTANT:
Do not claim that you opened an application, changed a setting,
sent a message, deleted a file, or performed any computer action
unless the Python program actually performed that action.

Keep normal answers short because your responses are spoken aloud.
"""


# ============================================================
# TEXT TO SPEECH
# ============================================================

engine = pyttsx3.init()

engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)


def speak(text):
    print(f"\nJARVIS: {text}")

    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("TTS error:", e)


# ============================================================
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8
recognizer.non_speaking_duration = 0.5


# ============================================================
# MICROPHONE CALIBRATION
# ============================================================

def initialize_microphone():

    try:

        microphone = sr.Microphone(device_index=MIC_ID)

        print(f"Microphone selected: ID {MIC_ID}")
        print("Calibrating microphone...")

        with microphone as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=2
            )

        print("Microphone ready.")

        return microphone

    except Exception as e:

        print("Microphone initialization error:", e)

        return None


# ============================================================
# LISTEN
# ============================================================

def listen(microphone):

    if microphone is None:
        return None

    try:

        print("\nListening...")

        with microphone as source:

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=10
            )

        print("Processing...")

        text = recognizer.recognize_google(audio)

        text = text.lower().strip()

        print(f"You: {text}")

        return text

    except sr.WaitTimeoutError:

        # No speech detected.
        # Stay silent instead of repeatedly saying
        # "I couldn't understand that."

        return None

    except sr.UnknownValueError:

        # Audio was detected but speech wasn't understood.
        return None

    except sr.RequestError:

        speak(
            "The speech recognition service is unavailable."
        )

        return None

    except Exception as e:

        print("Speech recognition error:", e)

        return None


# ============================================================
# WHATSAPP
# ============================================================

def open_whatsapp():

    print("Attempting to open WhatsApp...")

    # First try the Windows WhatsApp protocol.
    try:

        os.startfile("whatsapp:")

        speak("Opening WhatsApp.")

        return True

    except Exception as e:

        print("WhatsApp desktop launch failed:", e)

    # If the desktop app isn't available,
    # open WhatsApp Web instead.

    try:

        webbrowser.open("https://web.whatsapp.com")

        speak("Opening WhatsApp Web.")

        return True

    except Exception as e:

        print("WhatsApp Web launch failed:", e)

        speak("I couldn't open WhatsApp.")

        return True


# ============================================================
# APPLICATION LAUNCHER
# ============================================================

def open_application(app):

    applications = {

        "brave": [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
        ],

        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ],

        "vscode": [
            os.path.expandvars(
                r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"
            )
        ],

        "notepad": [
            "notepad.exe"
        ],

        "calculator": [
            "calc.exe"
        ],

        "explorer": [
            "explorer.exe"
        ]
    }


    if app == "whatsapp":

        return open_whatsapp()


    if app not in applications:

        return False


    possible_paths = applications[app]


    # Find a valid application path.

    for path in possible_paths:

        if (
            path.endswith(".exe")
            and not os.path.isabs(path)
        ):

            # Windows system commands such as notepad.exe
            # can be launched directly.

            try:

                subprocess.Popen(path)

                speak(f"Opening {app}.")

                return True

            except Exception:

                continue


        if os.path.exists(path):

            try:

                subprocess.Popen(path)

                speak(f"Opening {app}.")

                return True

            except Exception as e:

                print("Launch error:", e)


    # Special fallback for Windows commands.

    if app == "notepad":

        try:

            subprocess.Popen("notepad.exe")

            speak("Opening Notepad.")

            return True

        except Exception:
            pass


    if app == "calculator":

        try:

            subprocess.Popen("calc.exe")

            speak("Opening Calculator.")

            return True

        except Exception:
            pass


    if app == "explorer":

        try:

            subprocess.Popen("explorer.exe")

            speak("Opening File Explorer.")

            return True

        except Exception:
            pass


    speak(f"I couldn't find {app} on this PC.")

    return True


# ============================================================
# FOLDER LAUNCHER
# ============================================================

def open_folder(folder):

    folders = {

        "downloads":
            os.path.expandvars(
                r"%USERPROFILE%\Downloads"
            ),

        "documents":
            os.path.expandvars(
                r"%USERPROFILE%\Documents"
            ),

        "desktop":
            os.path.expandvars(
                r"%USERPROFILE%\Desktop"
            ),

        "pictures":
            os.path.expandvars(
                r"%USERPROFILE%\Pictures"
            ),

        "music":
            os.path.expandvars(
                r"%USERPROFILE%\Music"
            ),

        "videos":
            os.path.expandvars(
                r"%USERPROFILE%\Videos"
            )
    }


    if folder not in folders:

        return False


    path = folders[folder]


    try:

        os.startfile(path)

        speak(f"Opening {folder}.")

        return True

    except Exception as e:

        print("Folder error:", e)

        speak(f"I couldn't open {folder}.")

        return True


# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot():

    try:

        from PIL import ImageGrab

        screenshots_folder = os.path.expandvars(
            r"%USERPROFILE%\Pictures\Jarvis Screenshots"
        )

        os.makedirs(
            screenshots_folder,
            exist_ok=True
        )


        timestamp = datetime.datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )


        filename = os.path.join(
            screenshots_folder,
            f"screenshot_{timestamp}.png"
        )


        image = ImageGrab.grab()

        image.save(filename)


        print(f"Screenshot saved to:\n{filename}")

        speak("Screenshot captured.")

    except Exception as e:

        print("Screenshot error:", e)

        speak("I couldn't capture the screenshot.")


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def system_info():

    try:

        import psutil

        cpu = psutil.cpu_percent(
            interval=1
        )

        ram = psutil.virtual_memory().percent

        speak(
            f"CPU usage is {cpu:.0f} percent. "
            f"Memory usage is {ram:.0f} percent."
        )

    except Exception as e:

        print("System information error:", e)

        speak(
            "I couldn't retrieve system information."
        )


# ============================================================
# TIME
# ============================================================

def tell_time():

    current_time = datetime.datetime.now().strftime(
        "%I:%M %p"
    )

    speak(
        f"The current time is {current_time}."
    )


# ============================================================
# DATE
# ============================================================

def tell_date():

    current_date = datetime.datetime.now().strftime(
        "%A, %d %B %Y"
    )

    speak(
        f"Today is {current_date}."
    )


# ============================================================
# OPEN WEBSITE
# ============================================================

def open_website(command):

    websites = {

        "youtube":
            "https://www.youtube.com",

        "google":
            "https://www.google.com",

        "gmail":
            "https://mail.google.com",

        "instagram":
            "https://www.instagram.com",

        "github":
            "https://github.com",

        "whatsapp web":
            "https://web.whatsapp.com"
    }


    for name, url in websites.items():

        if f"open {name}" in command:

            try:

                webbrowser.open(url)

                speak(f"Opening {name}.")

                return True

            except Exception:

                speak(f"I couldn't open {name}.")

                return True


    return False


# ============================================================
# SEARCH WEB
# ============================================================

def search_web(command):

    prefixes = [
        "search for ",
        "search ",
        "google ",
        "look up "
    ]


    for prefix in prefixes:

        if command.startswith(prefix):

            query = command[len(prefix):].strip()

            if not query:
                return True


            url = (
                "https://www.google.com/search?q="
                + query.replace(" ", "+")
            )


            try:

                webbrowser.open(url)

                speak(
                    f"Searching the web for {query}."
                )

            except Exception:

                speak("I couldn't perform the search.")


            return True


    return False


# ============================================================
# HANDLE PC COMMANDS
# ============================================================

def handle_command(command):

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if command in [
        "exit",
        "quit",
        "shutdown jarvis",
        "goodbye jarvis",
        "go offline"
    ]:

        speak(
            "Shutting down. Goodbye."
        )

        sys.exit()


    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    if (
        "what time is it" in command
        or "current time" in command
        or command == "time"
    ):

        tell_time()

        return True


    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if (
        "what date is it" in command
        or "today's date" in command
        or "todays date" in command
        or command == "date"
    ):

        tell_date()

        return True


    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    if (
        "take a screenshot" in command
        or "take screenshot" in command
        or "capture my screen" in command
    ):

        take_screenshot()

        return True


    # --------------------------------------------------------
    # SYSTEM INFORMATION
    # --------------------------------------------------------

    if (
        "cpu usage" in command
        or "ram usage" in command
        or "memory usage" in command
        or "system usage" in command
    ):

        system_info()

        return True


    # --------------------------------------------------------
    # WEBSITE
    # --------------------------------------------------------

    if open_website(command):

        return True


    # --------------------------------------------------------
    # WEB SEARCH
    # --------------------------------------------------------

    if search_web(command):

        return True


    # --------------------------------------------------------
    # APPLICATIONS
    # --------------------------------------------------------

    applications = [
        "whatsapp",
        "brave",
        "chrome",
        "vscode",
        "notepad",
        "calculator",
        "explorer"
    ]


    for app in applications:

        if (
            f"open {app}" in command
            or f"launch {app}" in command
            or f"start {app}" in command
        ):

            return open_application(app)


    # --------------------------------------------------------
    # FOLDERS
    # --------------------------------------------------------

    folders = [
        "downloads",
        "documents",
        "desktop",
        "pictures",
        "music",
        "videos"
    ]


    for folder in folders:

        if (
            f"open {folder}" in command
            or f"open my {folder}" in command
        ):

            return open_folder(folder)


    return False


# ============================================================
# LOCAL AI BRAIN
# ============================================================

conversation = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


def ask_jarvis(message):

    conversation.append(
        {
            "role": "user",
            "content": message
        }
    )


    response = ollama.chat(
        model=MODEL,
        messages=conversation
    )


    reply = response["message"]["content"]


    conversation.append(
        {
            "role": "assistant",
            "content": reply
        }
    )


    return reply


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("                 J.A.R.V.I.S. v0.3")
    print("              LOCAL AI PC ASSISTANT")
    print("=" * 60)
    print()
    print(f"AI Model : {MODEL}")
    print(f"Mic ID   : {MIC_ID}")
    print()
    print("Available commands:")
    print("  • Open WhatsApp")
    print("  • Open Brave")
    print("  • Open Chrome")
    print("  • Open VS Code")
    print("  • Open Downloads")
    print("  • Take a screenshot")
    print("  • What time is it?")
    print("  • What is my CPU usage?")
    print("  • Search for something")
    print("  • Normal questions → Local Qwen AI")
    print("  • Goodbye Jarvis")
    print()


    # Initialize microphone once.
    microphone = initialize_microphone()


    if microphone is None:

        print()
        print("ERROR: Microphone could not be initialized.")
        print("Check the microphone settings and try again.")
        return


    speak(
        "Good evening. JARVIS is online."
    )


    while True:

        command = listen(microphone)


        if not command:

            continue


        # ----------------------------------------------------
        # Remove JARVIS prefix
        # ----------------------------------------------------

        if command.startswith("jarvis"):

            command = command[
                len("jarvis"):
            ].strip(" ,")


        # ----------------------------------------------------
        # Ignore empty commands
        # ----------------------------------------------------

        if not command:

            continue


        # ----------------------------------------------------
        # Execute computer commands
        # ----------------------------------------------------

        if handle_command(command):

            continue


        # ----------------------------------------------------
        # Otherwise use local AI
        # ----------------------------------------------------

        try:

            reply = ask_jarvis(command)

            speak(reply)

        except Exception as e:

            print()
            print("AI ERROR:", e)

            speak(
                "I encountered an error "
                "while processing that request."
            )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    main()