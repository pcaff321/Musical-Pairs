from .models import Audio_store, AudioRound, Mumble, Survey_James, User, TextRound, SurveyRound, Page, Experiment, Survey, SurveyQuestion, Word, WordBundle, set_file_name
from time import time
from faker import Faker
from django.conf import settings
import os
import string

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
    experiment = Experiment.objects.all()
    user = User.objects.all()
    if experiment.exists() and user.exists():
        return user[0], experiment[0]

    #Experiment.objects.all().delete()
    #Audio_store.objects.all().delete()
    
    fake = Faker()
    user = User(username=str(time()), password="joe", email=fake.ascii_safe_email(), first_name=fake.first_name_female(), last_name="PIETRO_WORDS", gender="Female", date_of_birth=fake.date_of_birth())
    user.save()

    experiment = Experiment(user_source=user, title="ExperimentTest")
    experiment.save()
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
