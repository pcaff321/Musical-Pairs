from django.db import models
from django.contrib.auth.models import AbstractUser
from faker import Faker
from time import time


from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# Create your models here.

def set_file_name(instance, user_id):
    if user_id is not None:
            print("inst name", instance.name)
            return '{0}/{1}'.format(str(user_id), str(instance.name))
    return 'user_{0}/{1}'.format(str(instance.name), str(instance.name))




class User(AbstractUser):
    is_researcher = models.BooleanField('researcher status', default=False)
    is_experimentee = models.BooleanField('experimentee status', default=True)
    date_of_birth = models.DateField('Date Of Birth', null=False)
    gender = models.CharField(max_length=30, null=False)
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    REQUIRED_FIELDS = ['date_of_birth', 'gender', 'first_name']

    def age(self):
            import datetime
            dob = self.date_of_birth
            tod = datetime.date.today()
            my_age = (tod.year - dob.year) - int((tod.month, tod.day) < (dob.month, dob.day))
            return my_age
    


class Experiment(models.Model):
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=False)


class Audio_store(models.Model):
    name = models.CharField(max_length=20, null=False, unique=True)
    allow_mumble = models.BooleanField(null=False, default=False)
    file_location=models.FileField(upload_to=set_file_name)
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table='Audio_store'


class Word(models.Model):
    word = models.CharField(max_length=20, null=False, unique=True)
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_store = models.ForeignKey(Audio_store, on_delete=models.CASCADE)


class ExperimentWord(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)


class Pair(models.Model):
    audio1 = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='Audio1')
    audio2 = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='Audio2')


class Audio_Answer(models.Model):
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    answer = models.CharField(max_length=20, null=False)
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

class Survey(models.Model):
    name = models.CharField(max_length=3000, null=False)
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)

class SurveyQuestion(models.Model):
    questionTypes = (
      (1, 'text'),
      (2, 'slider'),
      (3, 'yesOrNo')
    )
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    questionText = models.CharField(max_length=3000, null=False)
    questionType = models.PositiveSmallIntegerField(choices=questionTypes, default=1)
    questionNumber = models.IntegerField(max_length=100, null=False)


class SurveyRound(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, null=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)


class SurveyAnswer(models.Model):
    surveyQuestion = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.CharField(max_length=300, null=False)



## Audio model for a specific user(when randomly generated audio is made)
class UserAudioRound(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    audio_ref = models.ForeignKey(Audio_store, on_delete=models.CASCADE)
    for_user = models.ForeignKey(User, on_delete=models.CASCADE)
    roundNum = models.IntegerField(null=False)


class AudioRound(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)
    mumbles = models.BooleanField('mumbles', default=False)
    pairs = models.IntegerField(null=False)
    placebo = models.BooleanField('placebo', default=False)


class TextRound(models.Model):
    text = models.CharField(max_length=3000, null=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)


class Page(models.Model):
    page_number = models.IntegerField(max_length=100, null=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)

    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class UserProgress:
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page_number = models.IntegerField(max_length=100, null=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    text = models.CharField(max_length=3000, null=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
