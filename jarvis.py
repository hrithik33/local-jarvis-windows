# ============================================================
# JARVIS v0.6
# Gemini 3.8 Flash + Windows Control
# Classroom TEXT MODE
# ============================================================

import os
import re
import time
import webbrowser
import subprocess
import datetime
from pathlib import Path

import psutil

from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

MODEL = "gemini-3.8-flash"

THINKING_LEVEL = "low"

MAX_RETRIES = 3

APP_NAME = "JARVIS"


# ============================================================
# API KEY
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print()
    print("ERROR: GEMINI_API_KEY is not set.")
    print()
    print('Run:')
    print('$env:GEMINI_API_KEY="YOUR_KEY"')
    print()
    raise SystemExit(1)


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# JARVIS PERSONALITY
# ============================================================

SYSTEM_PROMPT = """
You are JARVIS, a personal AI assistant running on a Windows PC.

Your personality:
- Intelligent
- Calm
- Helpful
- Slightly futuristic
- Friendly
- Direct
- Concise when appropriate

You are the reasoning layer of a computer assistant.

Important rules:

1. Answer the user's questions naturally.

2. Do not pretend you performed a computer action unless the
   local JARVIS program actually performed that action.

3. Never claim to have opened an application, deleted a file,
   sent a message, changed a setting, or controlled Windows
   unless the local program confirmed it.

4. For simple questions, keep answers short.

5. For technical questions, explain clearly.

6. When asked for programming help, provide working code.

7. If the user asks a complicated question, reason carefully.

8. The user may interact with you through voice later, so avoid
   unnecessarily long responses.

9. You are JARVIS, not a generic chatbot.
"""


# ============================================================
# GEMINI CONFIG
# ============================================================

GEMINI_CONFIG = types.GenerateContentConfig(

    system_instruction=SYSTEM_PROMPT,

    thinking_config=types.ThinkingConfig(
        thinking_level=THINKING_LEVEL
    ),

    max_output_tokens=500,
)


# ============================================================
# CONVERSATION MEMORY
# ============================================================

conversation_history = []


def build_prompt(user_message):

    # Keep a lightweight local history.
    # This avoids an ever-growing request.

    recent_history = conversation_history[-10:]

    history_text = ""

    if recent_history:

        history_text = "\n\nPrevious conversation:\n"

        for role, message in recent_history:

            history_text += (
                f"{role}: {message}\n"
            )

    return (
        history_text
        + "\n\nCurrent user message:\n"
        + user_message
    )


# ============================================================
# GEMINI REQUEST
# ============================================================

def ask_gemini(question):

    prompt = build_prompt(question)

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            print()
            print("☁️  Gemini is thinking...")

            response = client.models.generate_content(

                model=MODEL,

                contents=prompt,

                config=GEMINI_CONFIG,
            )

            answer = response.text

            if not answer:

                return "I didn't receive a response."

            answer = answer.strip()

            conversation_history.append(
                ("User", question)
            )

            conversation_history.append(
                ("JARVIS", answer)
            )

            return answer

        except Exception as error:

            error_text = str(error)

            print()
            print(
                f"Gemini attempt "
                f"{attempt}/{MAX_RETRIES} failed."
            )

            print(error_text)

            # Retry temporary errors only.
            temporary = (

                "503" in error_text

                or "UNAVAILABLE" in error_text

                or "high demand" in error_text

                or "429" in error_text

                or "RESOURCE_EXHAUSTED" in error_text

                or "500" in error_text

            )

            if temporary and attempt < MAX_RETRIES:

                wait_time = 2 ** attempt

                print(
                    f"Retrying in "
                    f"{wait_time} seconds..."
                )

                time.sleep(wait_time)

                continue

            # Model/key errors shouldn't be retried.
            if "404" in error_text:

                return (
                    "The Gemini model is not available "
                    "for this API key."
                )

            if "401" in error_text:

                return (
                    "The Gemini API key was rejected."
                )

            if "403" in error_text:

                return (
                    "Gemini access was denied for this API key."
                )

            break

    return (
        "Gemini is temporarily unavailable. "
        "Please try again."
    )


# ============================================================
# TIME
# ============================================================

def get_time():

    now = datetime.datetime.now()

    return now.strftime("%I:%M %p")


def time_command():

    return (
        f"The time is {get_time()}."
    )


# ============================================================
# DATE
# ============================================================

def date_command():

    now = datetime.datetime.now()

    return (
        "Today is "
        + now.strftime("%A, %d %B %Y")
        + "."
    )


# ============================================================
# SYSTEM STATUS
# ============================================================

def system_status():

    cpu = psutil.cpu_percent(
        interval=0.2
    )

    memory = psutil.virtual_memory()

    disk = psutil.disk_usage("C:\\")

    result = []

    result.append(
        f"CPU usage is {cpu:.0f}%."
    )

    result.append(
        f"Memory usage is {memory.percent:.0f}%."
    )

    result.append(
        f"C drive usage is {disk.percent:.0f}%."
    )

    battery = psutil.sensors_battery()

    if battery:

        state = (
            "charging"
            if battery.power_plugged
            else "not charging"
        )

        result.append(
            f"Battery is {battery.percent:.0f}% "
            f"and {state}."
        )

    return " ".join(result)


# ============================================================
# OPEN APPLICATION
# ============================================================

def open_app(app):

    app = app.lower().strip()

    # --------------------------------------------------------
    # WHATSAPP
    # --------------------------------------------------------

    if "whatsapp" in app:

        try:

            os.startfile("whatsapp:")

            return "Opening WhatsApp."

        except Exception:

            webbrowser.open(
                "https://web.whatsapp.com"
            )

            return "Opening WhatsApp Web."

    # --------------------------------------------------------
    # SPOTIFY
    # --------------------------------------------------------

    if "spotify" in app:

        try:

            os.startfile("spotify:")

            return "Opening Spotify."

        except Exception:

            webbrowser.open(
                "https://open.spotify.com"
            )

            return "Opening Spotify in the browser."

    # --------------------------------------------------------
    # CHROME
    # --------------------------------------------------------

    if app in [
        "chrome",
        "google chrome",
    ]:

        chrome_paths = [

            r"C:\Program Files\Google\Chrome\Application\chrome.exe",

            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",

        ]

        for path in chrome_paths:

            if os.path.exists(path):

                subprocess.Popen(
                    [path]
                )

                return "Opening Chrome."

        try:

            subprocess.Popen(
                ["chrome"]
            )

            return "Opening Chrome."

        except Exception:

            return "I couldn't find Chrome."

    # --------------------------------------------------------
    # BRAVE
    # --------------------------------------------------------

    if app == "brave":

        brave_paths = [

            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",

            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",

        ]

        for path in brave_paths:

            if os.path.exists(path):

                subprocess.Popen(
                    [path]
                )

                return "Opening Brave."

        try:

            subprocess.Popen(
                ["brave"]
            )

            return "Opening Brave."

        except Exception:

            return "I couldn't find Brave."

    # --------------------------------------------------------
    # VS CODE
    # --------------------------------------------------------

    if app in [
        "vs code",
        "visual studio code",
        "vscode",
    ]:

        try:

            subprocess.Popen(
                ["code"]
            )

            return "Opening Visual Studio Code."

        except Exception:

            return (
                "I couldn't find "
                "Visual Studio Code."
            )

    # --------------------------------------------------------
    # NOTEPAD
    # --------------------------------------------------------

    if app == "notepad":

        subprocess.Popen(
            ["notepad.exe"]
        )

        return "Opening Notepad."

    # --------------------------------------------------------
    # CALCULATOR
    # --------------------------------------------------------

    if app in [
        "calculator",
        "calc",
    ]:

        subprocess.Popen(
            ["calc.exe"]
        )

        return "Opening Calculator."

    # --------------------------------------------------------
    # FILE EXPLORER
    # --------------------------------------------------------

    if app in [
        "explorer",
        "file explorer",
    ]:

        subprocess.Popen(
            ["explorer.exe"]
        )

        return "Opening File Explorer."

    return None


# ============================================================
# CLOSE APPLICATION
# ============================================================

def close_app(app):

    app = app.lower().strip()

    processes = {

        "chrome": [
            "chrome.exe"
        ],

        "google chrome": [
            "chrome.exe"
        ],

        "brave": [
            "brave.exe"
        ],

        "spotify": [
            "spotify.exe"
        ],

        "whatsapp": [
            "WhatsApp.exe",
            "WhatsAppHost.exe"
        ],

        "vs code": [
            "Code.exe"
        ],

        "visual studio code": [
            "Code.exe"
        ],

        "vscode": [
            "Code.exe"
        ],

        "notepad": [
            "notepad.exe"
        ],
    }

    if app not in processes:

        return (
            f"I don't have a close command "
            f"for {app}."
        )

    closed = False

    for process in processes[app]:

        try:

            result = subprocess.run(

                [
                    "taskkill",
                    "/IM",
                    process,
                    "/F",
                ],

                capture_output=True,
                text=True,
            )

            if result.returncode == 0:

                closed = True

        except Exception:

            pass

    if closed:

        return f"Closing {app}."

    return (
        f"{app} doesn't appear "
        f"to be running."
    )


# ============================================================
# FOLDERS
# ============================================================

def open_folder(folder):

    home = Path.home()

    folders = {

        "downloads":
            home / "Downloads",

        "download":
            home / "Downloads",

        "documents":
            home / "Documents",

        "document":
            home / "Documents",

        "desktop":
            home / "Desktop",

        "pictures":
            home / "Pictures",

        "photos":
            home / "Pictures",

        "music":
            home / "Music",

        "videos":
            home / "Videos",

    }

    folder = folder.lower().strip()

    if folder not in folders:

        return None

    try:

        os.startfile(
            str(folders[folder])
        )

        return (
            f"Opening {folder}."
        )

    except Exception:

        return (
            f"I couldn't open {folder}."
        )


# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot():

    try:

        from PIL import ImageGrab

        folder = (
            Path.home()
            / "Pictures"
            / "Jarvis Screenshots"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        timestamp = datetime.datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        path = (
            folder
            / f"jarvis_{timestamp}.png"
        )

        image = ImageGrab.grab()

        image.save(path)

        return (
            "Screenshot captured. "
            f"Saved to {path}"
        )

    except Exception as error:

        print(error)

        return (
            "I couldn't take "
            "the screenshot."
        )


# ============================================================
# WEBSITE
# ============================================================

def open_website(site):

    site = site.lower().strip()

    websites = {

        "youtube":
            "https://www.youtube.com",

        "google":
            "https://www.google.com",

        "gmail":
            "https://mail.google.com",

        "github":
            "https://github.com",

        "instagram":
            "https://www.instagram.com",

        "linkedin":
            "https://www.linkedin.com",

        "chatgpt":
            "https://chatgpt.com",

        "gemini":
            "https://gemini.google.com",

    }

    if site not in websites:

        return None

    webbrowser.open(
        websites[site]
    )

    return (
        f"Opening {site}."
    )


# ============================================================
# GOOGLE SEARCH
# ============================================================

def google_search(query):

    query = query.strip()

    if not query:

        return (
            "Tell me what you "
            "want me to search for."
        )

    url = (
        "https://www.google.com/search?q="
        + query.replace(" ", "+")
    )

    webbrowser.open(url)

    return (
        f"Searching Google for "
        f"{query}."
    )


# ============================================================
# HELP
# ============================================================

def show_help():

    print()
    print("=" * 65)
    print("                    JARVIS COMMANDS")
    print("=" * 65)

    print()
    print("SYSTEM")
    print("  what time is it")
    print("  state time")
    print("  what is today's date")
    print("  system status")
    print("  take screenshot")

    print()
    print("APPS")
    print("  open chrome")
    print("  open brave")
    print("  open spotify")
    print("  open whatsapp")
    print("  open vscode")
    print("  open notepad")
    print("  open calculator")

    print()
    print("FOLDERS")
    print("  open downloads")
    print("  open documents")
    print("  open desktop")
    print("  open pictures")
    print("  open music")
    print("  open videos")

    print()
    print("WEB")
    print("  search for artificial intelligence")
    print("  open youtube")
    print("  open github")

    print()
    print("AI")
    print("  who is Hardik Pandya?")
    print("  explain quantum computing")
    print("  write a C program")

    print()
    print("PROGRAM")
    print("  clear")
    print("  exit")

    print()
    print("=" * 65)
    print()


# ============================================================
# LOCAL COMMAND PROCESSOR
# ============================================================

def process_command(command):

    if not command:

        return True

    lower = command.lower().strip()

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if lower in [

        "exit",
        "quit",
        "goodbye",
        "goodbye jarvis",
        "exit jarvis",
        "quit jarvis",
        "stop jarvis",

    ]:

        print()
        print(
            "JARVIS: Going offline."
        )

        return False

    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    if lower == "help":

        show_help()

        return True

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    if lower == "clear":

        os.system("cls")

        print(
            "JARVIS v0.6"
        )

        print()

        return True

    # --------------------------------------------------------
    # GREETING
    # --------------------------------------------------------

    if lower in [

        "hello",
        "hi",
        "hey",
        "hello jarvis",
        "hi jarvis",
        "hey jarvis",

    ]:

        print()
        print(
            "JARVIS: Hello. "
            "How can I help?"
        )

        return True

    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    time_commands = [

        "time",
        "time please",
        "tell time",
        "state time",
        "what time",
        "what time is it",
        "what time is it now",
        "what is the time",
        "tell me the time",
        "current time",

    ]

    if lower in time_commands:

        print()
        print(
            "JARVIS:",
            time_command()
        )

        return True

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    date_commands = [

        "date",
        "today date",
        "today's date",
        "current date",
        "what is the date",
        "what is today's date",
        "tell me the date",

    ]

    if lower in date_commands:

        print()
        print(
            "JARVIS:",
            date_command()
        )

        return True

    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    if lower in [

        "system status",
        "pc status",
        "computer status",
        "system information",
        "computer information",
        "how is my computer",

    ]:

        print()
        print(
            "JARVIS:",
            system_status()
        )

        return True

    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    if lower in [

        "take screenshot",
        "take a screenshot",
        "capture screen",
        "capture screenshot",

    ]:

        print()
        print(
            "JARVIS:",
            take_screenshot()
        )

        return True

    # --------------------------------------------------------
    # FOLDER
    # --------------------------------------------------------

    folder_match = re.match(

        r"^(open|launch|start)\s+"
        r"(downloads?|documents?|desktop|"
        r"pictures?|photos?|music|videos?)$",

        lower,
    )

    if folder_match:

        result = open_folder(
            folder_match.group(2)
        )

        if result:

            print()
            print(
                "JARVIS:",
                result
            )

            return True

    # --------------------------------------------------------
    # OPEN
    # --------------------------------------------------------

    open_match = re.match(

        r"^(open|launch|start)\s+(.+)$",

        lower,
    )

    if open_match:

        target = (
            open_match
            .group(2)
            .strip()
        )

        # Website

        result = open_website(
            target
        )

        if result:

            print()
            print(
                "JARVIS:",
                result
            )

            return True

        # Application

        result = open_app(
            target
        )

        if result:

            print()
            print(
                "JARVIS:",
                result
            )

            return True

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------

    close_match = re.match(

        r"^(close|quit|exit)\s+(.+)$",

        lower,
    )

    if close_match:

        target = (
            close_match
            .group(2)
            .strip()
        )

        result = close_app(
            target
        )

        print()
        print(
            "JARVIS:",
            result
        )

        return True

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search_match = re.match(

        r"^(search for|google|look up)\s+(.+)$",

        lower,
    )

    if search_match:

        query = (
            search_match
            .group(2)
        )

        print()
        print(
            "JARVIS:",
            google_search(query)
        )

        return True

    # --------------------------------------------------------
    # EVERYTHING ELSE
    # --------------------------------------------------------
    # Send to Gemini.

    answer = ask_gemini(
        command
    )

    print()
    print("JARVIS:")
    print(answer)
    print()

    return True


# ============================================================
# STARTUP
# ============================================================

def print_banner():

    print()
    print("=" * 65)
    print("                    J A R V I S")
    print("                         v0.6")
    print("=" * 65)

    print()
    print("AI         :", MODEL)
    print("Thinking   :", THINKING_LEVEL)
    print("Interface  : TEXT")
    print("Microphone : OFF")
    print("Ollama     : OFF")
    print("Status     : ONLINE")

    print()
    print(
        "Type 'help' for commands."
    )

    print(
        "Type 'exit' to shut down JARVIS."
    )

    print()
    print("=" * 65)
    print()


# ============================================================
# MAIN
# ============================================================

def main():

    print_banner()

    print(
        "JARVIS: All systems online."
    )

    print(
        "JARVIS: Text interface ready."
    )

    print()

    while True:

        try:

            command = input(
                "You: "
            )

            if not process_command(
                command
            ):

                break

        except KeyboardInterrupt:

            print()
            print()
            print(
                "JARVIS: Going offline."
            )

            break

        except EOFError:

            print()
            break

        except Exception as error:

            print()
            print(
                "Unexpected error:"
            )

            print(error)

            print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()