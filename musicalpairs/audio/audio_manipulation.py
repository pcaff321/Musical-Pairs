from email.mime import audio
import os
from django.conf import settings

from pydub import AudioSegment, effects
from .models import Mumble, Pair, User, Word, Audio_store, set_file_name, ExperimentWord, UserWordRound, UserPairGuess
import requests
import tempfile
import random
from random import shuffle


silence = AudioSegment.silent(500)

cling = AudioSegment.from_wav(settings.MEDIA_ROOT + "/roundSounds/bell.wav")
music = AudioSegment.from_wav(settings.MEDIA_ROOT + "/roundSounds/delay_music_15_seconds.wav")

def makeMask(mumble, SPEEDUP_FACTOR=3):
    nonWord = AudioSegment.from_wav(str(settings.MEDIA_ROOT) + "/" + str(mumble)).speedup(SPEEDUP_FACTOR) - 18
    nonWord += AudioSegment.silent(50)
    return nonWord


def getNonWord(mumbles, SPEEDUP_FACTOR=3):
    mumble = mumbles.pop()
    nonWord = AudioSegment.from_wav(str(settings.MEDIA_ROOT) + "/" + str(mumble)).speedup(SPEEDUP_FACTOR) - 18
    nonWord += AudioSegment.silent(50)
    return mumbles, nonWord, str(mumble)


def getMask(mumbles, SPEEDUP_FACTOR=3):
    mumbles, mask, mumble = getNonWord(mumbles, SPEEDUP_FACTOR)
    return mumbles, mask, mumble


def isWordUsed(experiment, word):
    experimentWords = ExperimentWord.objects.filter(experiment=experiment)
    for word in experimentWords:
        if word.word == word:
            return True
    return False
    


def makeWordRound(wordsForRound, pairAmount=3, Experiment=None):
    global cling
    global music
    global silence
    pairs = list()
    fullAudio = None
    for i in range(pairAmount):
        word1 = wordsForRound.pop()
        while isWordUsed(Experiment, word1) and (len(wordsForRound) > 0):
            word1 = wordsForRound.pop()
        word2 = wordsForRound.pop()
        while isWordUsed(Experiment, word2) and (len(wordsForRound) > 0):
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
    pietro = User.objects.filter(last_name="PIETRO_WORDS")[0]
    words = Word.objects.filter(user_source=pietro)
    mumblesSet = Mumble.objects.all() ##  DO THIS - REMOVE / FIX
    mumbles = list()
    for mumble in mumblesSet:
        mumbles.append(str(mumble.audio_store.file_location))
    random.shuffle(mumbles)
    mumbles, firstMask, _ = getMask(mumbles)
    mumbles, X, _ = getMask(mumbles)
    if J is not None:
        X = J
    wordOne = str(pair.audio1.audio_store.file_location)
    firstAudio = AudioSegment.from_wav(str(settings.MEDIA_ROOT) + "/" + wordOne)
    finalAudio = AudioSegment.silent(2000) + firstMask + X + firstAudio
    if placebo:
        NON_WORDS_AMOUNT -= 1
    for i in range(NON_WORDS_AMOUNT):
        mumbles, mask, _ = getNonWord(mumbles)
        finalAudio += mask
    if placebo:
        wordTwo = settings.MEDIA_ROOT + "/" + str(pair.audio2.audio_store.file_location)
        secondAudio = AudioSegment.from_wav(wordTwo).speedup(1)
        finalAudio += secondAudio
    finalAudio += firstAudio
    for i in range(NON_WORDS_AMOUNT):
        mumbles, mask, _ = getNonWord(mumbles)
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
    words = Mumble.objects.all()
    for word in words:
        mumbles.append(word.audio_store.file_location)
    random.shuffle(mumbles)
    J_exp = None
    K_exp = None
    experiment = wordRound.experiment
    J_loc = experiment.j_mask
    K_loc = experiment.k_mask
    if J_loc == "_NONE_":
        mumbles, J_exp, loc = getMask(mumbles)
        experiment.j_mask = loc
        experiment.save()
    else:
        J_exp = makeMask(J_loc)

    if K_loc == "_NONE_":
        mumbles, K_exp, loc = getMask(mumbles)
        experiment.k_mask = loc
        experiment.save()
    else:
        K_exp = makeMask(K_loc)

    roundNum = 0
    for pair in pairsList:
        placebo = False
        J = None
        roundPrime = prime
        if prime == 'K':
            if random.random() <= 0.8:  # 20% chance placebo is used
                roundPrime = 'J'
        if roundPrime == 'J':
            J = J_exp
        elif roundPrime == 'K':
            J = K_exp
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

    audioRound = pageModel.content_object
    prime = audioRound.prime
    experiment_user = experiment.user_source

    pietro = User.objects.filter(last_name="PIETRO_WORDS")[0]
    user_bundle_source = audioRound.word_bundle.user_source
    words = list(Word.objects.filter(user_source=user_bundle_source))
    random.shuffle(words)
    wordRoundAudio, pairs = makeWordRound(words, pairAmount=pairs, Experiment=experiment)

    wordRoundName = "{}_{}_Page_{}.wav".format(user.id, experiment.id, pageModel.page_number)

    joinedPath = os.path.join(settings.MEDIA_ROOT, str(user_id), wordRoundName)
    print("JOIND PATH", joinedPath)

    
    path1 = os.path.join(settings.MEDIA_ROOT, str(user_id))
    #path2 = os.path.join(path1, wordRoundName)

    # Check whether the specified path exists or not
    isExist = os.path.exists(path1)

    if not isExist:
    
        os.makedirs(path1)
        print("The new directory is created!")

    exported = wordRoundAudio.export(out_f = joinedPath, format = "wav").name
    #exported = wordRoundAudio.export(out_f = (settings.MEDIA_ROOT + "/" + str(user_id) + "/" + wordRoundName) + ".wav", format = "wav").name

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
