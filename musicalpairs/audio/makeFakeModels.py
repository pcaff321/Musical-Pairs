from .models import Audio_store, AudioRound, Survey_James, User, TextRound, SurveyRound, Page, Experiment, Survey, SurveyQuestion
from time import time
from faker import Faker
from django.conf import settings

def create_Fake_Models():

    Experiment.objects.all().delete()
    Audio_store.objects.all().delete()
    
    fake = Faker()
    user = User(username=str(time()), password="joe", email=fake.ascii_safe_email(), first_name=fake.first_name_female(), last_name="joe", gender="Female", date_of_birth=fake.date_of_birth())
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
    question = SurveyQuestion(user_source=user, survey=survey, questionText="Hello", questionType=1, questionNumber=1)
    question.save()
    surveyRound = SurveyRound(survey=survey, experiment=experiment, user_source=user)
    surveyRound.save()

    #testAudio = Audio_store(name="SampleAudio", allow_mumble=False, file_location=settings.MEDIA_URL+"/TEST_USER/combinedAudio.wav", user_source=user)
    #testAudio.save()

    audioRound = AudioRound(experiment=experiment, mumbles=False, pairs=5, placebo=False, user_source=user)
    audioRound.save()

    rounds = [textRound, textRound1, audioRound, textRound2, surveyRound, textRound3]

    page_num = 1
    for round in rounds:
        new_page = Page(page_number=page_num, experiment=experiment, content_object=round, user_source=user)
        new_page.save()
        page_num += 1




    print("Fake models created")
    return user, experiment
