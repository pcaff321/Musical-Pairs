from django import forms 
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from time import time
from crispy_forms.helper import FormHelper

class DateInput(forms.DateInput):
    input_type = 'date'

#class AudioForm(forms.ModelForm):
#    class Meta:
#        model=Audio_store
#        fields=['name', 'allow_mumble', 'file_location']

class AudioForm(forms.Form):
    word = forms.CharField(max_length=40)
    file = forms.FileField()


class CustomAuthenticationForm(AuthenticationForm):
    class Meta():
        widgets = {
            'username' : forms.TextInput(attrs={'class':'form-control'}),
            'password' : forms.TextInput(attrs={'class':'form-control'}),
        }


class ResearcherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'gender']

        widgets = {
            'first_name' : forms.TextInput(attrs={'placeholder':'First Name'}),
            'last_name' : forms.TextInput(attrs={ 'placeholder':'Last Name'}),
            'email' : forms.EmailInput(attrs={ 'placeholder':'Your Email'}),
            'date_of_birth' : DateInput(),
            'gender' : forms.TextInput(attrs={'placeholder':'Gender'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'placeholder': ("Password")})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'placeholder': ("Re-Type Password")})
        self.helper = FormHelper(self)
        self.helper.form_show_labels = False


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
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'gender', 'password1', 'password2']
    class Meta:
        widgets = {
            'first_name' : forms.TextInput(attrs={'class':'form-control input'}),
            'last_name' : forms.TextInput(attrs={'class':'form-control'}),
            'email' : forms.TextInput(attrs={'class':'form-control'}),
            'date_of_birth' : DateInput(attrs={'class':'form-control'}),
            'gender' : forms.TextInput(attrs={'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'placeholder': ("Password")})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'placeholder': ("Re-Type Password")})
        self.helper = FormHelper(self)
        self.helper.form_show_labels = False


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

class PublishForm(forms.Form):
    experiment = forms.ModelChoiceField(widget=forms.Select(attrs={'class' : 'form-select'}), queryset=Experiment.objects.all().order_by('title'))
    subject = forms.CharField(label="subject", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Subject'}))
    body = forms.CharField(label="body", max_length=1000)
    body= forms.CharField(label="body", max_length=1000, widget=forms.Textarea(attrs={"class":"form-control sm-text-area", 'placeholder':'E-Mail Body'}))

class PublishForm2(forms.Form):
    subject = forms.CharField(label="subject", max_length=100, widget=forms.TextInput(attrs={'class':'form-control inputs', 'placeholder':'Subject'}))
    body= forms.CharField(label="body", max_length=1000, widget=forms.Textarea(attrs={"class":"form-control sm-text-area inputs", 'placeholder':'E-Mail Body'}))
