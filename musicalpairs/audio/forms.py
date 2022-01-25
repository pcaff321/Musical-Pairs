from django import forms 
from .models import *
from django.contrib.auth.forms import UserCreationForm

class AudioForm(forms.ModelForm):
    class Meta:
        model=Audio_store
        fields=['name', 'allow_mumble', 'file_location']


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