from email.mime import audio
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import AudioForm, ResearcherSignUpForm, ExperimenteeSignUpForm
from .models import User, set_file_name, Audio_store, Word
from .audio_manipulation import combineAudios
from .serializers import Audio_serializer
from rest_framework.renderers import JSONRenderer
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.db import models




# Create your views here.

def main(request):
    return HttpResponse("Test")
    

""" @login_required
def Audio_store(request):
    if request.method == 'POST': 
        form = AudioForm(request.POST,request.FILES or None) 
        if form.is_valid(): 
            audio_store_instance = form.save(commit=False) 
            file_location = set_file_name(audio_store_instance, request.user.id)
            audio_store_instance.file_location.name = file_location
            audio_store_instance.save()
            combineAudios()
            serializer = Audio_serializer(audio_store_instance)
            json = JSONRenderer().render(serializer.data)
            return HttpResponse(str(json))
    else: 
        form = AudioForm() 
    return render(request, 'aud.htm', {'form' : form})  """


@login_required
def Audio_store_view(request):
    if request.method == 'POST': 
        form = AudioForm(request.POST,request.FILES or None) 
        if form.is_valid(): 
            print("stuff: \n")
            word = form.cleaned_data['word']
            audio_name = "{}_{}".format(request.user.id, word)
            audio_file = form.cleaned_data['file']
            print(audio_name)

            #Make audio store object
            audio_store_instance = Audio_store(name=audio_name, allow_mumble=False, file_location=audio_file, user_source=request.user)
            file_location = set_file_name(audio_store_instance, request.user.id)
            audio_store_instance.file_location.name = file_location
            audio_store_instance.save()

            # Make associated Word object
            associated_word_instance = Word(word=word, user_source=request.user, audio_store=audio_store_instance)
            associated_word_instance.save()


            return redirect(showAudios)
    else: 
        form = AudioForm() 
    return render(request, 'aud.htm', {'form' : form}) 


@login_required
def playAudioFile(request):
    user_id = request.user.id
    url = settings.MEDIA_URL + "user_{}/{}.wav".format(user_id, "twattwattwat")
    return render(request, 'playAudio.html', {'link': url })

@login_required
def showAudios(request):
    user_id = request.user.id
    audios_of_user = Audio_store.objects.filter(user_source=request.user)
    for instance in audios_of_user:
        instance.file_location = settings.MEDIA_URL + str(instance.file_location)
    context = {
        "object_list": audios_of_user
    }
    return render(request, 'showAudios.html', context)


def loginView(request):
    return render(request, 'login.html')


class experimentee_signup(CreateView):
    model = User
    form_class = ExperimenteeSignUpForm
    template_name = 'signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'experimentee'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(playAudioFile)


class researcher_signup(CreateView):
    model = User
    form_class = ResearcherSignUpForm
    template_name = 'signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'researcher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(Audio_store)


    
def logout_view(request):
    logout(request)
    return redirect("/signup/experimentee/")