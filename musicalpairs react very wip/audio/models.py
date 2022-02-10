from django.db import models
from django.contrib.auth.models import AbstractUser
import string
import random

# Create your models here.

def set_file_name(instance, filename):
    return 'user_{0}/{1}.wav'.format(str(instance.word), str(instance.word))

class Audio_store(models.Model):
    word = models.CharField(max_length=20, null=False, unique=True)
    allow_mumble = models.BooleanField(null=False, default=False)
    record=models.FileField(upload_to=set_file_name)
    class Meta:
        db_table='Audio_store'


class User(AbstractUser):
    is_researcher = models.BooleanField('researcher status', default=False)
    is_experimentee = models.BooleanField('experimentee status', default=True)

def generate_unique_code():
    length = 6 

    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if Survey.objects.filter(code=code).count() == 0:
            break
    
    return code

class Survey(models.Model):
    code = models.CharField(max_length=8, default=generate_unique_code, unique=True)
    host = models.CharField(max_length=50)
    name = models.CharField(null=False, max_length=50, default="Default")
    # guest_can_pause = models.BooleanField(null=False, default=False)
    # votes_to_skip = models.IntegerField(null=False, default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    round_count = models.IntegerField(null=False, default=2)
    round_list = models.JSONField(default=dict)

'''class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)'''
