from email.mime import audio
from django.conf import settings

from pydub import AudioSegment, effects
from .models import Pair, Word, Audio_store, set_file_name, ExperimentWord, UserWordRound, UserPairGuess
import requests
import tempfile
import random
from random import shuffle


silence = AudioSegment.silent(500)

cling = AudioSegment.from_wav(settings.MEDIA_ROOT + "/roundSounds/bell.wav")
music = AudioSegment.from_wav(settings.MEDIA_ROOT + "/roundSounds/delay_music_15_seconds.wav")


def getNonWord(mumbles, SPEEDUP_FACTOR=3):
    mumble = mumbles.pop()
    print(mumble)
    nonWord = AudioSegment.from_wav(str(settings.MEDIA_ROOT) + "/" + str(mumble)).speedup(SPEEDUP_FACTOR) - 18
    nonWord += AudioSegment.silent(50)
    return mumbles, nonWord


def getMask(mumbles, SPEEDUP_FACTOR=3):
    mumbles, mask = getNonWord(mumbles, SPEEDUP_FACTOR)
    return mumbles, mask



def makeWordRound(wordsForRound, pairAmount=3, Experiment=None):
    global cling
    global music
    global silence
    pairs = list()
    fullAudio = None
    for i in range(pairAmount):
        word1 = wordsForRound.pop()
        word2 = wordsForRound.pop()
        pair = Pair(audio1=word1, audio2=word2)
        pair.save()
        pairs.append(pair)
        word1Location = settings.MEDIA_ROOT + "/" + str(word1.audio_store.file_location)
        word2Location = settings.MEDIA_ROOT + "/" + str(word2.audio_store.file_location)
        audio1 = AudioSegment.from_wav(word1Location)
        audio2 = AudioSegment.from_wav(word2Location)
        if fullAudio is None:
            fullAudio = cling
        else:
            fullAudio += cling
        fullAudio += silence + audio1 + silence
        fullAudio += audio2 + silence
    fullAudio += AudioSegment.silent(2500) + music
    return fullAudio, pairs


def makeBaselineRound(pair, mumbles, J=None, placebo=False, wordRound=None):
    global cling
    global silence
    NON_WORDS_AMOUNT = 4
    words = Word.objects.all()
    mumbles = list() ##  DO THIS - REMOVE / FIX
    for word in words:
        mumbles.append(str(word.audio_store.file_location))
    """mumbles = list()
    for word in words:
        mumbles.append(word.audio_ref.file_location.url + ".wav") """
    mumbles, firstMask = getMask(mumbles)
    mumbles, X = getMask(mumbles)
    if J is not None:
        X = J
    wordOne = str(pair.audio1.audio_store.file_location)
    firstAudio = AudioSegment.from_wav(str(settings.MEDIA_ROOT) + "/" + wordOne)
    finalAudio = AudioSegment.silent(2000) + firstMask + X + firstAudio
    if placebo:
        NON_WORDS_AMOUNT -= 1
    for i in range(NON_WORDS_AMOUNT):
        mumbles, mask = getNonWord(mumbles)
        finalAudio += mask
    if placebo:
        wordTwo = settings.MEDIA_ROOT + "/" + str(pair.audio2.audio_ref.file_location)
        secondAudio = AudioSegment.from_wav(wordTwo).speedup(1)
        finalAudio += secondAudio
    finalAudio += firstAudio
    for i in range(NON_WORDS_AMOUNT):
        mumbles, mask = getNonWord(mumbles)
        finalAudio += mask
    finalAudio += silence
            
    return finalAudio, mumbles


def makeBaselineRounds(pairs, wordRound, prime):
    b_rounds = list()
    user = wordRound.for_user
    user_id = user.id
    pairsList = pairs.copy()
    random.shuffle(pairsList) # Have pairs in random order
    mumbles = list()
    words = Word.objects.all()
    for word in words:
        mumbles.append(word.audio_store.file_location)
    roundNum = 0
    for pair in pairsList:
        placebo = False
        J = None
        roundPrime = prime
        if prime == 'K':
            if random.random() <= 0.8:  # 20% chance placebo is used
                roundPrime = 'J'
        if roundPrime == 'J':
            J = None
        elif roundPrime == 'K':
            J = None
            placebo = True
        # J must be sent as a mumbled word
        b_round, mumbles = makeBaselineRound(pair, mumbles, J=J, placebo=placebo, wordRound=wordRound)
        roundNum += 1
        pairRoundName = "{}_{}_Round_{}.wav".format(pair.audio1.word, pair.audio2.word, wordRound.id)
        fileName = str(pairRoundName)
        exported = b_round.export(out_f = settings.MEDIA_ROOT + "/" + str(user_id) + "/" + fileName, format="wav").name

        pairGuessAudio = Audio_store(name=fileName, allow_mumble=False, file_location=exported, user_source=user)
        file_location = set_file_name(pairGuessAudio, user.id)
        pairGuessAudio.file_location.name = file_location
        pairGuessAudio.save()
        
        userPairGuess = UserPairGuess(pair=pair, audio_ref=pairGuessAudio, associated_word_round=wordRound, placebo_added=placebo, prime=roundPrime)
        userPairGuess.save()

        b_rounds.append(userPairGuess)

    return b_rounds
        


def makeAudioRounds(mumbles=False, pairs=5, placebo=False, user=None, experiment=None, pageModel=None):

    user_id = None
    if user is None:
        user_id = 12345
    else:
        user_id = user.id

    prime = pageModel.content_object.prime
    experiment_user = experiment.user_source

    words = list(Word.objects.filter(user_source=experiment_user))
    wordRoundAudio, pairs = makeWordRound(words, pairAmount=pairs, Experiment=experiment)

    wordRoundName = "{}_{}_Page_{}.wav".format(user.id, experiment.id, pageModel.page_number)

    exported = wordRoundAudio.export(out_f = (settings.MEDIA_ROOT + "/" + str(user_id) + "/" + wordRoundName) + ".wav", format = "wav").name

    wordRoundAudio = Audio_store(name=wordRoundName, allow_mumble=False, file_location=exported, user_source=user)
    file_location = set_file_name(wordRoundAudio, user.id)
    wordRoundAudio.file_location.name = file_location
    wordRoundAudio.save()

    wordRoundInstance = UserWordRound(experiment=experiment, audio_ref=wordRoundAudio, for_user=user, associated_audio_round=pageModel.content_object)
    wordRoundInstance.save()

    guess_rounds = makeBaselineRounds(pairs, wordRoundInstance, prime)

    roundAudios = list()
    roundAudios.append(wordRoundInstance)
    for i in guess_rounds:
        roundAudios.append(i)

    return roundAudios   #wordRoundAudio.file_location.url + ".wav"



#Dumb function, ignore
def getWord(user, used_words):
    print("words",  Word.objects.filter(user_source=user))
    return Word.objects.filter(user_source=user)[0]

def getWords(experiment):
    words = ExperimentWord.objects.filter(experiment=experiment)
    if not words.exist():
        words = Word.objects.filter(user_source=experiment.user_source)
    return list(words)


def makeRoundAudio(mumbles=False, pairs=5, placebo=False, user=None, experiment=None):
    user_id = None
    if user is None:
        user_id = 12345
    else:
        user_id = user.id
    mumbles = True
    amount = 5
    audio1 = None
    temp = tempfile.TemporaryFile()
    try:
        words_for_pairing = getWords(experiment)
        if (len(words_for_pairing) < (pairs * 2)):
            words_for_pairing = list()
            for i in range(pairs*2):
                words_for_pairing.append(getWord(user, None))  # FIX THIS: Just a workaround in case theres too little words, but awful solution
        final_audio = None #music
        for i in range(pairs):
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

def getRoundFile(mumbles=False, pairs=5, placebo=False, user=None, experiment=None, pageModel=None):
    return makeAudioRounds(mumbles, pairs, placebo, user, experiment, pageModel)
