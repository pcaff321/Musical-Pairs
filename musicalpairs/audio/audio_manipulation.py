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

def getMumbleWords(amount=4):
    random.shuffle(words)
    mumbled_words = list()
    for mumble in range(amount):
        mumbled_words.append(words[mumble])
    return mumbled_words.copy()


def getNonWord(mumbles, SPEEDUP_FACTOR=3):
    print("Words 3", len(mumbles))
    nonWord = AudioSegment.from_wav(mumbles.pop()).speedup(SPEEDUP_FACTOR) - 18
    nonWord += AudioSegment.silent(50)
    return mumbles, nonWord


def getMask(mumbles, SPEEDUP_FACTOR=3):
    print("Words 2", len(mumbles))
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


def makeBaselineRound(pair, J=None, placebo=False, roundAudio=None, wordRound=None):
    global cling
    global silence
    NON_WORDS_AMOUNT = 4
    words = Word.objects.all()
    mumbles = list()
    for word in words:
        mumbles.append(settings.MEDIA_ROOT + "/" + word.audio_ref.file_location)
    mumbles, firstMask = getMask(mumbles)
    mumbles, X = getMask(mumbles)
    if J is not None:
        X = J
    wordOne = pair.audio1.audio_ref.file_location
    firstAudio = AudioSegment.from_wav(wordOne)
    finalAudio = AudioSegment.silent(2000) + firstMask + X + firstAudio
    if placebo:
        NON_WORDS_AMOUNT -= 1
    for i in range(NON_WORDS_AMOUNT):
        mumbles, mask = getNonWord(mumbles)
        finalAudio += mask
    if placebo:
        wordTwo = settings.MEDIA_ROOT + "/" + pair.audio2.audio_ref.file_location
        secondAudio = AudioSegment.from_wav(wordTwo).speedup(1)
        finalAudio += secondAudio
    finalAudio += firstAudio
    for i in range(NON_WORDS_AMOUNT):
        mumbles, mask = getNonWord(mumbles)
        finalAudio += mask
    finalAudio += silence
    
    userPairGuess = UserPairGuess(pair=pair, audio_ref=roundAudio, associated_word_round=wordRound, placebo_added=placebo)
        
    return userPairGuess


def makeBaselineRounds(pairs, roundAudio, wordRound):
    b_rounds = list()
    for pair in pairs:
        b_round = makeBaselineRound(pair, J=None, placebo=False, roundAudio=roundAudio, wordRound=wordRound)
        b_rounds.append(b_round)
    roundNum = 0
    random.shuffle(b_rounds)
    for round in b_rounds:
        roundNum += 1
        round.export(out_f = "./{}B_Round.wav".format(roundNum), format="wav")
    return b_rounds


def makeAudioRounds(mumbles=False, pairs=5, placebo=False, user=None, experiment=None, pageModel=None):

    user_id = None
    if user is None:
        user_id = 12345
    else:
        user_id = user.id

    words = list(Word.objects.filter(user_source=user))
    wordRoundAudio, pairs = makeWordRound(words, pairAmount=pairs, Experiment=experiment)

    wordRoundName = "{}_{}_Page_{}.wav".format(user.id, experiment.id, pageModel.page_number)

    exported = wordRoundAudio.export(out_f = (settings.MEDIA_ROOT + "/" + str(user_id) + "/" + wordRoundName) + ".wav", format = "wav").name

    wordRoundAudio = Audio_store(name=wordRoundName, allow_mumble=False, file_location=exported, user_source=user)
    file_location = set_file_name(wordRoundAudio, user.id)
    wordRoundAudio.file_location.name = file_location
    wordRoundAudio.save()

    wordRoundInstance = UserWordRound(experiment=experiment, audio_ref=wordRoundAudio, for_user=user, associated_audio_round=pageModel.content_object)

    return '/media/1/1_4_Page_3.wav.wav' #wordRoundAudio.file_location.url + ".wav"



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
    #music = requests.get("https://github.com/Pietro-Rizzo/words_and_nonwords_1/blob/main/delay_music_15_seconds.wav?raw=true")
    audio1 = None
    temp = tempfile.TemporaryFile()
    try:
        #temp.write(music.content)
        #temp.seek(0)
        #music = AudioSegment.from_wav(temp)
        words_for_pairing = getWords(experiment)#.shuffle() # randomise for unique pairs
        if (len(words_for_pairing) < (pairs * 2)):
            words_for_pairing = list()
            for i in range(pairs*2):
                words_for_pairing.append(getWord(user, None))  # FIX THIS: Just a workaround in case theres too little words, but awful solution
        final_audio = None #music
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

def getRoundFile(mumbles=False, pairs=5, placebo=False, user=None, experiment=None, pageModel=None):
    return makeAudioRounds(mumbles, pairs, placebo, user, experiment, pageModel)
