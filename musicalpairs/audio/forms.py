from django import forms 
from .models import *
from django.contrib.auth.forms import UserCreationForm

class AudioForm(forms.ModelForm):


    class Meta:
        model=Audio_store
        fields=['word', 'allow_mumble', 'record']


class ResearcherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_experimentee = True
        user.is_researcher = True
        if commit:
            user.save()
        return user

class ExperimenteeSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_experimentee = True
        if commit:
            user.save()
        return user

class PublishForm(forms.Form):
    experiment = forms.ModelChoiceField(queryset=Experiment.objects.all().order_by('title'))
    subject = forms.CharField(label="subject", max_length=100)
    body = forms.CharField(label="body", max_length=1000)

