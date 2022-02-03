from django.conf import settings

from pydub import AudioSegment, effects
import requests
import tempfile

firstWord = settings.MEDIA_ROOT + "/user_fileTwo23/fileTwo23.wav"
secondWord = settings.MEDIA_ROOT + "/user_fileTwo23/fileTwo23.wav"

def makeMumbles():
    global firstWord
    audio1 =  AudioSegment.from_wav(firstWord)
    mumbledWord = audio1.speedup(4)
    backgroundNoise = mumbledWord
    for i in range(5):
        backgroundNoise += mumbledWord
    return backgroundNoise


def combineAudios():
    global firstWord
    global secondWord
    audio1 = AudioSegment.from_wav(firstWord)
    audio2 = AudioSegment.from_wav(secondWord)
    audio3 = audio1 + audio2
    backgroundNoise = makeMumbles()
    audio3 = audio3.overlay(backgroundNoise)
    audio3.export(out_f = (settings.MEDIA_ROOT + "/user_fileTwo23/" + "combinedAudio.wav"), format = "wav")


def makeRoundAudio():
    user = "TEST_USER"
    mumbles = True
    amount = 5
    music = requests.get("https://github.com/Pietro-Rizzo/words_and_nonwords_1/blob/main/delay_music_15_seconds.wav?raw=true")
    audio1 = None
    temp = tempfile.TemporaryFile()
    try:
        temp.write(music.content)
        temp.seek(0)
        audio1 = AudioSegment.from_wav(temp)
        audio1.export(out_f = (settings.MEDIA_ROOT + "/" + user + "/combinedAudio.wav"), format = "wav")
    finally:
        temp.close()
    return settings.MEDIA_ROOT + "/" + user + "/combinedAudio.wav"

def getRoundFile():
    return makeRoundAudio()
