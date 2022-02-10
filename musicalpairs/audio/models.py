from django.db import models
from django.contrib.auth.models import AbstractUser


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

class Experiment(models.Model):
    user_source = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    title = models.CharField(max_length=50, null=False)
    subscribers = models.ManyToManyField(User, related_name="sub")
