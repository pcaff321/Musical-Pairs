from django.conf import settings

from pydub import AudioSegment, effects
from .models import Pair, Word, Audio_store, set_file_name
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


def makeRoundAudio_OLD():
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


def getWord(user, used_words):
    print("User")
    print("words",  Word.objects.filter(user_source=user))
    return Word.objects.filter(user_source=user)[0]

def makeRoundAudio(mumbles=False, pairs=5, placebo=False, user=None):
    user_id = None
    if user is None:
        user_id = 12345
    else:
        user_id = user.id
    mumbles = True
    amount = 5
    #music = requests.get("https://github.com/Pietro-Rizzo/words_and_nonwords_1/blob/main/delay_music_15_seconds.wav?raw=true")
    audio1 = None
    temp = tempfile.TemporaryFile()
    try:
        #temp.write(music.content)
        #temp.seek(0)
        #music = AudioSegment.from_wav(temp)
        words_for_pairing = list()
        final_audio = None #music
        for i in range(pairs*2):
            print("Getting words", i, pairs)
            words_for_pairing.append(getWord(user, words_for_pairing))
        for i in range(pairs):
            print("MAking audio", i)
            word1 = words_for_pairing.pop()
            word2 = words_for_pairing.pop()
            pair = Pair(audio1=word1, audio2=word2)
            pair.save()
            word1Audio = AudioSegment.from_wav(settings.MEDIA_ROOT + "/" + str(word1.audio_store.file_location))
            word2Audio = AudioSegment.from_wav(settings.MEDIA_ROOT + "/" + str(word2.audio_store.file_location))
            cling = word2Audio.speedup(5)
            if final_audio is None:
                final_audio = cling
            final_audio += cling
            final_audio += (word1Audio + word2Audio + cling)
        #final_audio += music

        print("exporting audio")

        exported = final_audio.export(out_f = (settings.MEDIA_ROOT + "/" + str(user_id) + "/combinedAudio.wav"), format = "wav").name

        audio_store_instance = Audio_store(name="combinedAudio", allow_mumble=False, file_location=exported, user_source=user)
        file_location = set_file_name(audio_store_instance, user.id)
        audio_store_instance.file_location.name = file_location
        audio_store_instance.save()

    finally:
        temp.close()
    return settings.MEDIA_ROOT + "/" + str(user_id) + "/combinedAudio.wav"

def getRoundFile(mumbles=False, pairs=5, placebo=False, user=None):
    return makeRoundAudio(mumbles, pairs, placebo, user)
