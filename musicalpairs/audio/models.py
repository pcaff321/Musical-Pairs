from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from datetime import datetime
from django.conf import settings



# Create your models here.

def set_file_name(instance, filename):
    return 'user_{0}/{1}.wav'.format(str(instance.name), str(instance.name))

class User(AbstractUser):
    email = models.EmailField(('email address'), max_length=254)
    is_researcher = models.BooleanField('researcher status', default=False)
    is_experimentee = models.BooleanField('experimentee status', default=True)


class Audio_store(models.Model):
    name = models.CharField(max_length=20, null=False, unique=True)
    allow_mumble = models.BooleanField(null=False, default=False)
    file_location=models.FileField(upload_to=set_file_name, default="test.wav")



