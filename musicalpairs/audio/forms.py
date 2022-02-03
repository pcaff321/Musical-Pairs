from django import forms 
from .models import *
from django.contrib.auth.forms import UserCreationForm
from time import time

class DateInput(forms.DateInput):
    input_type = 'date'

#class AudioForm(forms.ModelForm):
#    class Meta:
#        model=Audio_store
#        fields=['name', 'allow_mumble', 'file_location']

class AudioForm(forms.Form):
    word = forms.CharField(max_length=40)
    file = forms.FileField()


class ResearcherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'gender']
        widgets = {
            'date_of_birth': DateInput()
        }


    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_experimentee = True
        user.is_researcher = True
        user.username = time()
        if commit:
            user.save()
        return user

class ExperimenteeSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'gender', 'password']
        widgets = {
            'date_of_birth': DateInput()
        }


    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_experimentee = True
        if commit:
            user.save()
        return user


class PostForm(forms.ModelForm):
    class Meta:
        # exclude = ['author', 'updated', 'created', ]
        fields = ['text']