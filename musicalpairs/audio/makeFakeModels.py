import random
from typing import Text
from .processRoundData import createAudioRound, createPage, createSurveyQuestion, createSurveyRound, createTextRound
from .models import Audio_store, AudioRound, ImageRound, Mumble, Pair, Survey_James, SurveyAnswer, User, TextRound, SurveyRound, Page, Experiment, Survey, SurveyQuestion, UserPairGuess, UserWordRound, Word, WordBundle, set_file_name
from time import time
from faker import Faker
from django.conf import settings
import os
import string


g_experiment = None


def makeFakeUser():
    fake = Faker()
    user = None
    if (random.randint(0, 3) < 2):
        user = User(username=str(time()), password="joe", 
        email=fake.ascii_safe_email(), first_name=fake.first_name_female(), 
        last_name=fake.first_name_male(), gender="Female",
        date_of_birth=fake.date_of_birth())
        user.save()
    else:
        user = User(username=str(time()), password="joe", 
        email=fake.ascii_safe_email(), first_name=fake.first_name_male(), 
        last_name=fake.first_name_male(), gender="Male",
        date_of_birth=fake.date_of_birth())
        user.save()
    return user

try:
    fakeUser = makeFakeUser()
    audioLoc = os.path.join(settings.MEDIA_ROOT, "fakeAudio.wav")
    fakeAudio = Audio_store(name="fakeAudio", allow_mumble=False, file_location=audioLoc, user_source=fakeUser)
    fakeAudio.save()
except:
    print("Database not created yet")


def getWordBundle(user):
    userBundle = WordBundle.objects.filter(user_source=user)
    if userBundle.exists():
        userBundle = userBundle[0]
    else:
        userBundle = WordBundle(name="Your Audios", public=False, user_source=user)
        userBundle.save()
    return userBundle

def makeExperiment(roundList):
    global g_experiment
    user = User.objects.filter(last_name="PIETRO_WORDS")[0]
    experiment = Experiment.objects.filter(user_source=user, title="Musical Pairs")
    if experiment.exists() and (len(Page.objects.filter(experiment=experiment[0])) > 20):
        print("Experiment Exists")
        fakeAnswersForExperiment(experiment[0], 30)
        return
    else:
        experiment = Experiment(user_source=user, title="Musical Pairs")
        experiment.save()
    pageNum = 1
    for data in roundList:

        if data['roundType'] == "survey":
            name = data['name']
            questions = data['questions']

            survey = Survey(name=name, user_source=user)
            survey.save()

            questionNumber = 1

            for question in questions:
                questionText = question['questionText']
                questionType = question['questionType']
                question = createSurveyQuestion(user, survey, questionText, questionType, questionNumber)
                questionNumber += 1

            round = createSurveyRound(experiment, survey, user)

        elif data['roundType'] == "audio":
            prime = str(data['prime'])
            pairs = int(data['pairs'])
            bundleId = data['bundleID']
            wordBundle = WordBundle.objects.filter(id=bundleId)
            if wordBundle.exists():
                wordBundle = wordBundle[0]
            else:
                wordBundle = getWordBundle(user)
            round = createAudioRound(pairs, prime, experiment, user, wordBundle)
        elif data['roundType'] == "text":
            title = data['title']
            text = data['text']
            round = createTextRound(title, text, experiment, user)


        if round is not None:
            new_page = createPage(experiment, pageNum, round, user)
            pageNum += 1
        else:
            print("round none")

    fakeAnswersForExperiment(experiment, 30)


def replicateMusicalPairs():
    user = User.objects.filter(last_name="PIETRO_WORDS")[0]
    wordBundle = WordBundle.objects.filter(name="Default Audios", public=True, user_source=user)
    if not wordBundle.exists():
        wordBundle = WordBundle(name="Default Audios", public=True, user_source=user)
        wordBundle.save()  
    else:
        wordBundle = wordBundle[0]
    roundList = list()
    # Round 1
    data = {
        "roundType": "text",
        "title": "What does the study involve?",
        "text": "It chiefly involves listening to isolated words, and then writing some of them in a second moment.\
            It also comprises listening to music and answering a few questions, mostly about feelings and one's outlook on life."
    }
    roundList.append(data)

    data = {
        "roundType": "text",
        "title": "Expected Duration",
        "text": "The whole session takes about an hour.\
            Note: Due to testing purposes, rounds can be skipped"
    }
    roundList.append(data)

    data = {
        "roundType": "text",
        "title": "Safety",
        "text": "Participation in this experiment is safe. There is no reason to expect participating\
            may evoke any feeling of discomfort, nor negative emotions. Participants' responses are collected anonymously.\
                 Participation may be freely interrupted at any moment and is completely voluntary."
    }
    roundList.append(data)

    data = {
        "roundType": "text",
        "title": "What is the study about?",
        "text": "This experiment explores the effect of music on speech processing - that is why participants ply several rounds \
            of a game called Musical Pairs. Because this is an experiment in the field of psychology, you cannot be told in advance \
                which exact hypothesis is being tested ( not before you participate - your knowledge would compromise the results \
                    Thank you for understanding."
    }
    roundList.append(data)

    data = {
        "roundType": "text",
        "title": "Further notes",
        "text": "The psychological phenomenon investigated in this experiment is one of the most interesting ones I have ever come across \
            during my years as a psychology student. Once you reach the end of the experiment, you will be told all about this phenomenon, and \
                how your participation in this experiment will help us understand it better."
    }
    roundList.append(data)

    data = {
        "roundType": "text",
        "title": "Keep In Touch",
        "text": "Should you wish to keep up to date with any further updates or news on this study, \
            please feel free to subscribe to updates at the end of this experiment or get in contact with me."
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Can you participate?",
        "text": "You may only participate if you have never taken part in this study before and you \
            believe that you will remain reasonably free from distractions during the course of this experiment"
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Can you participate?",
        "text": "You may only participate if you have never taken part in this study before and you \
            believe that you will remain reasonably free from distractions during the course of this experiment"
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Consent?",
        "text": "If you continue from this point, you hereby give consent to part in this study."
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Introduction To Musical Pairs",
        "text": "During this study, you will be asked to try your skill in a few rounds of Musical Pairs. \
            The following pages will outline what you must do"
    }
    roundList.append(data)

    data = {
        "roundType": "text",
        "title": "First Step",
        "text": "First, you will close your eyes and hear several word pairs. Each pair is preceded by a chime. For example - you may hear 'mirror . . . dog'. In this case, \
            'mirror' is the first word of a pair and 'dog' is the second word of a pair."
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Second Step",
        "text": "Next, you will listen to some music. This is played after all word pairs in a round have been played aloud. "
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Third Step",
        "text": "Finally, the first word of each pair will be played twice, and you will have to write down the corresponding second word. \
            For example - you would hear 'mirror . . . mirror' and you would type 'dog'"
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Tip",
        "text": "You will hear many pairs in one go, so you will need a way to connect words. Let's say the pair was 'fig . . . boat', \
            a strategy to memorise this pair could be imagining a boat full of figs! Always try to se the pairs in your mind like that."
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Tip",
        "text": "You will hear many pairs in one go, so you will need a way to connect words. Let's say the pair was 'fig . . . boat', \
            a strategy to memorise this pair could be imagining a boat full of figs! Always try to se the pairs in your mind like that."
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "One Last Note!",
        "text": "You will notice that there are mumbled 'distorted nonwords' in rounds where you must guess the second word. These are used to act as \
            'background noise' as if you were in a crowded area in the real world, such as the cafeteria, where there may be some background chatter. \
                Our brains process words in a particular way when they are heard close to other speech-like sounds, and it is that particular way of neural\
                    processing that I am interested in."
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Let's Begin!",
        "text": "There will be fewer tips now, so get ready to listen to some audios! \
            Remember the order: 'chime...word 1...word 2'"
    }
    roundList.append(data)


    data = {
        "roundType": "audio",
        "pairs": 12,
        "bundleID": wordBundle.id,
        "prime": "X"
    }
    roundList.append(data)



    data = {
        "roundType": "text",
        "title": "First Round Complete!",
        "text": "Congratulations on completing the first round! You have 2 more rounds to go! You may take a short 5-10 minute break \
            before proceeding."
    }
    roundList.append(data)


    data = {
        "roundType": "audio",
        "pairs": 12,
        "bundleID": wordBundle.id,
        "prime": "K"
    }
    roundList.append(data)

    data = {
        "roundType": "text",
        "title": "Second Round Complete!",
        "text": "You have one more round to go, then you are done! You may take a short 5-10 minute break before proceeding."
    }
    roundList.append(data)


    data = {
        "roundType": "audio",
        "pairs": 12,
        "bundleID": wordBundle.id,
        "prime": "J"
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Listening complete!",
        "text": "The listening rounds are complete. Thank you for your participation. I would now like to ask you a few follow-up questions \
            before we conclude."
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Notice Anything Strange?",
        "text": "You may have noticed that in later rounds, you might have heard a 'compressed' verison of the second word being played before the repeated first \
            word. I'm sorry I couldn't tell you beforehand, that was part of my testing!"
    }
    roundList.append(data)


    data = {
        "roundType": "survey",
        "name": "Mumbled Words",
        "questions": [{"questionText": "Did you notice the mumbled second words?", "questionType": 3}]
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "A Few Surveys",
        "text": "You are nearly done. Please just fill out the surveys on the following pages and then you are finished!"
    }
    roundList.append(data)


    data = {
        "roundType": "text",
        "title": "Aftermath Survey",
        "text": "The following questions concern the Musical Pairs round you just completed. From your answers, I hope to get a better sense of your experience.\
            Please indicate to what extent you agree with the following statements, using the response format: \
                0 = strongly disagree, 1 = disagree, 2 = neutral, 3 = agree, 4 = strongly agree.\
                    Please be accurate and honest in your answers."
    }
    roundList.append(data)


    data = {
        "roundType": "survey",
        "name": "Aftermatch Survey",
        "questions": [{"questionText": "During Musical Pairs, I put forward my best effort.", "questionType": 4},
            {"questionText": "During Musical Pairs, I felt absorbed.", "questionType": 4},
            {"questionText": "During Musical Pairs, I was well-focused.", "questionType": 4},
            {"questionText": "During Musical Pairs, I had some unrelated thoughts.", "questionType": 4},
            {"questionText": "During Musical Pairs, I was interrupted.", "questionType": 4},
            {"questionText": "During Musical Pairs, I felt tired.", "questionType": 4},
            {"questionText": "During Musical Pairs, the environment around me was quiet.", "questionType": 4},
            {"questionText": "During Musical Pairs, some noise around me made it harder for me to understand the words.", "questionType": 4},
            {"questionText": "During Musical Pairs, I kept my eyes closed whenever either words or music were played.", "questionType": 4},
            {"questionText": "During Musical Pairs, through Step 1, I tried to visualise each pair as an image in my mind.", "questionType": 4},
            {"questionText": "During Musical Pairs, as the music played, I just listened, thinking of nothing in particular.", "questionType": 4}
    
        ]
    }
    roundList.append(data)


    data = {
        "roundType": "survey",
        "name": "Word Quality",
        "questions": [{"questionText": "During Musical Pairs, I put forward my best effort.", "questionType": 4},
            {"questionText": "During Musical Pairs, the sound was crisp.", "questionType": 4},
            {"questionText": "During Musical Pairs the words sounded somewhat distorted, or metallic.", "questionType": 4},
            {"questionText": "During Musical Pairs, the words played were words I am familiar with.", "questionType": 4},
            {"questionText": "During Musical Pairs, some of the words were new to me.", "questionType": 4},
            {"questionText": "During Musical Pairs, the words were pronounced clearly.", "questionType": 4},
            {"questionText": "During Musical Pairs, the words were pronounced with a rather heavy accent.", "questionType": 4},
            {"questionText": "During Musical Pairs, the way words were pronounced made them harder to understand.", "questionType": 4}
    
        ]
    }
    roundList.append(data)

    makeExperiment(roundList)










def makePietroWords():
    print("MAKING PIETRO AUDIOSSSSSSSSSS")
    user = User.objects.filter(last_name="PIETRO_WORDS")[0]
    wordBundle = WordBundle.objects.filter(name="Default Audios", public=True, user_source=user)
    if not wordBundle.exists():
        print("IT DOES NOT EXISTTTTTTTTTTTTTTT")
        userBundle = WordBundle(name="Default Audios", public=True, user_source=user)
        userBundle.save()
    #Make audio store object
    words = Word.objects.filter(user_source=user)
    if len(words) > 50:
        return
    path = settings.MEDIA_ROOT + '/pietroWords/'
    print("PATH", path)
    files = os.listdir(path)
    print("FILES", files)

    for index, file in enumerate(files):
        name = str(file)
        word = os.path.splitext(name)[0]
        file_loc = os.path.join(settings.MEDIA_ROOT, name)
        audio_store_instance = Audio_store(name=word, allow_mumble=False, file_location=file_loc, user_source=user)
        file_location = set_file_name(audio_store_instance, user.id)
        audio_store_instance.file_location.name = 'pietroWords/' + name
        audio_store_instance.save()

        # Make associated Word object
        associated_word_instance = Word(word=word, user_source=user, audio_store=audio_store_instance)
        associated_word_instance.save()
    


def makeMumbleWords():
    #Make audio store object
    user = User.objects.filter(last_name="PIETRO_WORDS")[0]
    mumbles = Mumble.objects.filter(user_source=user)
    if len(mumbles) > 50:
        return
    path = settings.MEDIA_ROOT + '/NonWords/'
    files = os.listdir(path)

    for index, file in enumerate(files):
        name = str(file)
        word = os.path.splitext(name)[0]
        file_loc = os.path.join(settings.MEDIA_ROOT, name)
        audio_store_instance = Audio_store(name=word, allow_mumble=False, file_location=file_loc, user_source=user)
        file_location = set_file_name(audio_store_instance, user.id)
        audio_store_instance.file_location.name = 'NonWords/' + name
        audio_store_instance.save()

        # Make associated Word object
        associated_word_instance = Mumble(mumble=word, user_source=user, audio_store=audio_store_instance)
        associated_word_instance.save()


def create_Fake_Models():
    global g_experiment
    experiment = Experiment.objects.all()
    user = User.objects.all()
    if experiment.exists() and user.exists():
        g_experiment = experiment[0]
        return user[0], experiment[0]

    #Experiment.objects.all().delete()
    #Audio_store.objects.all().delete()
    
    fake = Faker()
    user = User(username=str(time()), password="joe", email=fake.ascii_safe_email(), first_name=fake.first_name_female(), last_name="PIETRO_WORDS", gender="Female", date_of_birth=fake.date_of_birth())
    user.save()

    experiment = Experiment(user_source=user, title="ExperimentTest")
    experiment.save()
    g_experiment = experiment
    print("Fake id", experiment.id)
    textRound = TextRound(text="Welcome To The Experiment", experiment=experiment, user_source=user)
    textRound.save()
    textRound1 = TextRound(text="Please Close Your Eyes And Click Any Button", experiment=experiment, user_source=user)
    textRound1.save()
    textRound2 = TextRound(text="Please Answer The Questions on The Next Page", experiment=experiment, user_source=user)
    textRound2.save()
    textRound3 = TextRound(text="Thank You For Doing The Experiment", experiment=experiment, user_source=user)
    textRound3.save()
    survey = Survey(name="TestSurvey", user_source=user)
    survey.save()
    question = SurveyQuestion(user_source=user, survey=survey, questionText="HelloINPUT", questionType=1, questionNumber=1)
    question.save()
    question = SurveyQuestion(user_source=user, survey=survey, questionText="HelloSLIDER", questionType=2, questionNumber=2)
    question.save()
    question = SurveyQuestion(user_source=user, survey=survey, questionText="HelloYES", questionType=3, questionNumber=3)
    question.save()
    surveyRound = SurveyRound(survey=survey, experiment=experiment, user_source=user)
    surveyRound.save()

    #testAudio = Audio_store(name="SampleAudio", allow_mumble=False, file_location=settings.MEDIA_URL+"/TEST_USER/combinedAudio.wav", user_source=user)
    #testAudio.save()

    audioRound = AudioRound(experiment=experiment, mumbles=False, pairs=5, placebo=False, user_source=user)
    audioRound.save()

    userBundle = WordBundle(name="Default Audios", public=True, user_source=user)
    userBundle.save()
    rounds = [textRound, textRound1, audioRound, textRound2, surveyRound, textRound3]

    page_num = 1
    for round in rounds:
        new_page = Page(page_number=page_num, experiment=experiment, content_object=round, user_source=user)
        new_page.save()
        page_num += 1

    print("Fake models created")
    return user, experiment



def fakeAnswersForSurvey(user, survey, experiment, inputAnswers=None):
    if inputAnswers is None:
        inputAnswers = ["happy", "sad", "easy", "hard", "depressed", "excited", "high", "drunk", "groovy"]
    questions = SurveyQuestion.objects.filter(survey=survey)
    for question in questions:
        questionType = question.questionType
        inputAns = "NOT_ANSWERED"
        if questionType == 1:
            inputAns = random.choice(inputAnswers)
        elif questionType == 2:
            inputAns = random.randint(0, 10)
        elif questionType == 3:
            yesOrNo = "Yes"
            if (random.randint(0, 3) < 2):
                yesOrNo = "No"
            inputAns = yesOrNo
        elif questionType == 4:
            inputAns = random.randint(1, 5)
        newAns = SurveyAnswer(surveyQuestion=question, experiment=experiment, user_source=user, answer=inputAns)
        newAns.save()

def fakeAnswersForAudio(user, audioRound, experiment, words):
    global fakeAudio
    word1 = words.pop()
    word2 = words.pop()
    pair = Pair(audio1=word1, audio2=word2)
    pair.save()
    wordRoundInstance = UserWordRound(experiment=experiment, audio_ref=fakeAudio, for_user=user, associated_audio_round=audioRound)
    wordRoundInstance.save()
    prime = audioRound.prime
    placebo = False
    roundPrime = prime
    if prime == 'K':
        if random.random() <= 0.8:  # 20% chance placebo is used
            roundPrime = 'J'
    if roundPrime == 'K':
        placebo = True

    userPairGuess = UserPairGuess(pair=pair, audio_ref=fakeAudio, associated_word_round=wordRoundInstance, placebo_added=placebo, prime=roundPrime)
    if placebo:
        if (random.randint(1, 10) <= 8):
            userPairGuess.answer = word2.word
    else:
        if (random.randint(1, 10) <= 6):
            userPairGuess.answer = word2.word
    if (random.randint(1, 10) <= 2):
            userPairGuess.answer = "NO_IDEA"
    if (random.randint(1, 10) <= 1):
            userPairGuess.answer = "WAS_DISTURBED"
    if (random.randint(1, 10) <= 1):
            userPairGuess.answer = "NOT_ANSWERED"
    userPairGuess.save()


def fakeAnswersForExperiment(experiment, amount_of_users):
    pietro = User.objects.filter(last_name="PIETRO_WORDS")[0]
    fakeDataMade = TextRound.objects.filter(title="FAKE ANSWERS MADE", experiment=experiment)
    userRounds = UserWordRound.objects.filter(experiment=experiment)
    if (len(fakeDataMade) > 0) and (len(userRounds) > 5):
        print("Fake models exist already")
        return
    print("Making fake data of {} users".format(amount_of_users))
    pages = Page.objects.filter(experiment=experiment)#.order_by('page_number')
    pagesList = list()
    for i in range(amount_of_users):
        words = list(Word.objects.filter(user_source=pietro))
        random.shuffle(words)
        print("Generating fake data for User {}".format(str(i)))
        user = makeFakeUser()
        for page in pages:
            if isinstance(page.content_object, ImageRound) or isinstance(page.content_object, SurveyRound):
                fakeAnswersForSurvey(user, page.content_object.survey, experiment)
            if isinstance(page.content_object, AudioRound):
                fakeAnswersForAudio(user, page.content_object, experiment, words)
    fakeModelsExist = TextRound(title="FAKE ANSWERS MADE", text="FAKE ANSWERS MADE", experiment=experiment, user_source=pietro)
    fakeModelsExist.save()