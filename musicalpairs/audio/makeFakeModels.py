from .models import Audio_store, AudioRound, User, TextRound, SurveyExample, Page, Experiment
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
    textRound = TextRound(text="Welcome To The Experiment", experiment=experiment)
    textRound.save()
    textRound1 = TextRound(text="Please Close Your Eyes And Click Any Button", experiment=experiment)
    textRound1.save()
    textRound2 = TextRound(text="Please Answer The Questions on The Next Page", experiment=experiment)
    textRound2.save()
    textRound3 = TextRound(text="Thank You For Doing The Experiment", experiment=experiment)
    textRound3.save()
    surveyRound = SurveyExample(text="Survey Test", experiment=experiment)
    surveyRound.save()

    testAudio = Audio_store(name="SampleAudio", allow_mumble=False, file_location=settings.MEDIA_URL+"/TEST_USER/combinedAudio.wav", user_source=user)
    testAudio.save()
    audioRound = AudioRound(experiment=experiment, audio_ref=testAudio)
    audioRound.save()

    rounds = [textRound, textRound1, audioRound, textRound2, surveyRound, textRound3]

    page_num = 1
    for round in rounds:
        new_page = Page(page_number=page_num, experiment=experiment, content_object=round)
        new_page.save()
        page_num += 1

    print("Fake models created")
    return user
