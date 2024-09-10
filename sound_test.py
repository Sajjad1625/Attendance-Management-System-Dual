import subprocess
import os

AUDIO_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio_data/')
# os.system(f"""ffmpeg -i "{AUDIO_FOLDER}Unknown.mp3" "{AUDIO_FOLDER}Unknown.wav" """)

import winsound

filename = AUDIO_FOLDER+'Unknown.wav'
winsound.PlaySound(filename, winsound.SND_FILENAME)

# from pydub import AudioSegment
# from pydub.playback import play
# print(AUDIO_FOLDER)
# sound = AudioSegment.from_wav(AUDIO_FOLDER)
# play(sound)

##AUDIO_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio_data/')
##print(AUDIO_FOLDER)
##subprocess.call(['ffmpeg', '-i', "Unknown.mp3", "Unknown.wav"])





# import pyttsx3
# engine = pyttsx3.init(driverName='sapi5')
# engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
# voices = engine.getProperty('voices')
# for i in voices:
#     print(i.id)
# to_speak = "Hello Vaibhav Sir"
# engine.say("  . "+to_speak)
# engine.runAndWait()
