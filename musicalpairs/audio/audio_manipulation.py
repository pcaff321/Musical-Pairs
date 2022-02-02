from django.conf import settings

from pydub import AudioSegment, effects

firstWord = settings.MEDIA_ROOT + "\\boat.wav"
secondWord = settings.MEDIA_ROOT + "\\figs.wav"

def makeMumbles():
    global firstWord
    audio1 =  AudioSegment.from_wav(firstWord)
    audio2 = AudioSegment.from_wav(secondWord)
    mumbleFast1 = audio1.speedup(3)
    mumbleFast2 = audio2.speedup(3)
    mumbledWord1 = mumbleFast1.reverse()
    mumbledWord2 = mumbleFast2.reverse()
    backgroundNoise = mumbledWord1 
    for i in range(3):
        backgroundNoise += mumbledWord2
        backgroundNoise += mumbledWord1
        
    return backgroundNoise


def combineAudios():
    print("MEDIA_ROOT:", settings.MEDIA_ROOT)
    global firstWord
    global secondWord
    print("FIRST", firstWord)
    audio1 = AudioSegment.from_wav(firstWord)
    audio2 = AudioSegment.from_wav(secondWord)
    audio3 = audio1 + audio2
    backgroundNoise = makeMumbles()
    audio3 = audio3.overlay(backgroundNoise)
    audio3.export(out_f = (settings.MEDIA_ROOT + "\combinedAudio.wav"), format = "wav")
    print("Combining")

