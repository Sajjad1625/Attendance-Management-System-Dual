import requests
import sqlite3
import os
from gtts import gTTS
import winsound
import time
import pyttsx3


AUDIO_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio_data/')
DATA_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'shared_data/')


spoken_dict = dict()

def test_internet(url = "http://www.google.com?device=FaceRecognitionMarriLaxmanReddyCollege"):
    try:
        request = requests.get(url, timeout=2)
        return 1
    except (requests.ConnectionError, requests.Timeout) as exception:
        return 0

def speak(ID):
    
    if ID == "Unknown":
        try:
            if 'Unknown.wav' in os.listdir(AUDIO_FOLDER):
                winsound.PlaySound(f'{AUDIO_FOLDER}Unknown.wav', winsound.SND_FILENAME)
            else:
                print("Generating Audio for Unknown")
                to_speak = "Welcome to AI LAB."
                if test_internet():
                    tts = gTTS(to_speak, tld="co.in", slow = 0)
                    tts.save(AUDIO_FOLDER+'Unknown.mp3')
                    time.sleep(0.1)
                    os.system(f"""ffmpeg -i "{AUDIO_FOLDER}Unknown.mp3" "{AUDIO_FOLDER}Unknown.wav" """)
                    os.remove(f"{AUDIO_FOLDER}Unknown.mp3")
                    winsound.PlaySound(AUDIO_FOLDER+'Unknown.wav', winsound.SND_FILENAME)
                else:
                    engine = pyttsx3.init(driverName='sapi5')
                    engine.setProperty('voice', r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
                    engine.say("  . "+to_speak)
                    engine.runAndWait()
        except Exception as e:
            print("Play Sound Error: ", e)
    else:
        if ID in spoken_dict.keys():
            last_time = spoken_dict[ID]
        else:
            spoken_dict[ID] = time.time()-30
            last_time = spoken_dict[ID]

        if time.time() - last_time >= 30:
            
            conn = sqlite3.connect('data.db')
            cursor = conn.execute(f"SELECT MESSAGE from USER where ID = '{ID}'")
            for row in cursor:
                to_speak = row[0]
            conn.close()
            try:
                if f'{ID}.wav' in os.listdir(AUDIO_FOLDER):
                    winsound.PlaySound(f'{AUDIO_FOLDER}{ID}.wav', winsound.SND_FILENAME)
                    spoken_dict[ID] = time.time()
                else:
                    print("Generating Audio")
                    if test_internet():
                        tts = gTTS(to_speak, tld="co.in", slow = 0)
                        tts.save("{AUDIO_FOLDER}{ID}.mp3")
                        time.sleep(0.1)
                        os.system(f"""ffmpeg -i "{AUDIO_FOLDER}{ID}.mp3" "{AUDIO_FOLDER}{ID}.wav" """)
                        os.remove(f"{AUDIO_FOLDER}{ID}.mp3")
                        winsound.PlaySound(AUDIO_FOLDER+'Unknown.wav', winsound.SND_FILENAME)
                        spoken_dict[ID] = time.time()
                    else:
                        engine = pyttsx3.init(driverName='sapi5')
                        engine.setProperty('voice', r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
                        engine.say("  . "+to_speak)
                        engine.runAndWait()
                        spoken_dict[ID] = time.time()
            except Exception as e:
                print("Play Sound Error: ", e)
        else:
            print("Greeted Recently: ", ID)

def main():
    time.sleep(10)
    while True:
        f1 = open(DATA_FOLDER+"speak_greetings.txt", 'r')
        speak_data = f1.read()
        f1.close()
        time.sleep(0.1)
        f1 = open(DATA_FOLDER+"speak_greetings.txt", 'w')
        f1.close()

        IDs = speak_data.strip().split("\n")
        unknown_count = IDs.count("Unknown")
        IDs = list(set(IDs))
        if 0 < unknown_count < 4:
            IDs.remove("Unknown")
        print(IDs)
        for ID in IDs:
            if len(ID) > 0:
                speak(ID)
        time.sleep(10)

speak("Unknown")