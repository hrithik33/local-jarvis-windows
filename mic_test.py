import speech_recognition as sr

MIC_ID = 1

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

print(f"Testing microphone ID {MIC_ID}")

try:
    with sr.Microphone(device_index=MIC_ID) as source:
        print("Calibrating...")
        recognizer.adjust_for_ambient_noise(source, duration=2)

        print("Speak now...")
        audio = recognizer.listen(
            source,
            timeout=10,
            phrase_time_limit=8
        )

    print("Processing...")

    text = recognizer.recognize_google(audio)

    print("\n==============================")
    print("YOU SAID:", text)
    print("==============================")

except sr.WaitTimeoutError:
    print("No speech detected.")

except sr.UnknownValueError:
    print("Audio was detected, but I couldn't understand it.")

except sr.RequestError as e:
    print("Speech recognition service error:", e)

except Exception as e:
    print("ERROR:", type(e).__name__, "-", e)