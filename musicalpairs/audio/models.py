from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

def set_file_name(instance, user_id):
    if user_id is not None:
            return '{0}/{1}.wav'.format(str(user_id), str(instance.name))
    return 'user_{0}/{1}.wav'.format(str(instance.name), str(instance.name))




class User(AbstractUser):
    is_researcher = models.BooleanField('researcher status', default=False)
    is_experimentee = models.BooleanField('experimentee status', default=True)
    date_of_birth = models.DateField('Date Of Birth', null=False)
    gender = models.CharField(max_length=30, null=False)
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()

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


class Pair(models.Model):
    audio1 = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='Audio1')
    audio2 = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='Audio2')


class Audio_Answer(models.Model):
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    answer = models.CharField(max_length=20, null=False)
    user_source = models.ForeignKey(User, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    