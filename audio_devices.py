import speech_recognition as sr
import pyaudio

p = pyaudio.PyAudio()

print("\n=== AVAILABLE INPUT DEVICES ===\n")

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)

    if info["maxInputChannels"] > 0:
        print(
            f"ID: {i} | "
            f"Inputs: {info['maxInputChannels']} | "
            f"Rate: {int(info['defaultSampleRate'])} | "
            f"Name: {info['name']}"
        )

p.terminate()