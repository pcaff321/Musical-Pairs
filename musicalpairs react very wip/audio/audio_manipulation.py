from django.conf import settings

from pydub import AudioSegment, effects

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
    print("FIRST", firstWord)
    audio1 = AudioSegment.from_wav(firstWord)
    audio2 = AudioSegment.from_wav(secondWord)
    audio3 = audio1 + audio2
    backgroundNoise = makeMumbles()
    audio3 = audio3.overlay(backgroundNoise)
    audio3.export(out_f = (settings.MEDIA_ROOT + "/user_fileTwo23/" + "combinedAudio.wav"), format = "wav")
    print("Combining")
