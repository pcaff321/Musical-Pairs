##from curses.ascii import HT
from email.mime import audio
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import AudioForm, ResearcherSignUpForm, ExperimenteeSignUpForm
from .models import User, set_file_name, Audio_store, Word, Experiment, Page, SurveyExample, AudioRound, TextRound
from .audio_manipulation import combineAudios, getRoundFile
from .serializers import Audio_serializer
from rest_framework.renderers import JSONRenderer
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.db import models
import json
import re

from .makeFakeModels import create_Fake_Models


print("CALLING CREATE FAKE MODELS")
fake_user = create_Fake_Models()



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


def Audio_store_view(request):
    print("Success ATTEMPT")
    if request.method == 'POST': 
        form = AudioForm(request.POST,request.FILES or None) 
        print("POSTED")
        print(request.POST)
        print("Files:", request.FILES)
        print(form)
        if form.is_valid(): 
            global fake_user
            user = fake_user # request.user
            print("stuff: \n")
            word = form.cleaned_data['word']
            audio_name = "{}_{}".format(request.user.id, word)
            audio_file = form.cleaned_data['file']
            print(audio_name)

            #Make audio store object
            audio_store_instance = Audio_store(name=audio_name, allow_mumble=False, file_location=audio_file, user_source=user)
            file_location = set_file_name(audio_store_instance, user.id)
            audio_store_instance.file_location.name = file_location
            audio_store_instance.save()

            # Make associated Word object
            associated_word_instance = Word(word=word, user_source=user, audio_store=audio_store_instance)
            associated_word_instance.save()


            return redirect(showAudios)
    else: 
        form = AudioForm() 
    return render(request, 'aud.htm', {'form' : form}) 


@login_required
def playAudioFile(request):
    user_id = request.user.id
    url = settings.MEDIA_URL + "user_{}/{}.wav".format(user_id, "lalala")
    return render(request, 'playAudio.html', {'link': url })

def getPage(experimentID, pageNumber):
    experiment = Experiment.objects.filter(title=experimentID)[0]
    print("EXPER", experiment)
    pages = Page.objects.filter(experiment=experiment, page_number=pageNumber)
    if len(pages) <= 0:
        return None
    return pages[0]



def prevRoundPage(request):
    sessionNum = request.session.get('sessionNum', 0)
    sessionNum -= 1
    if sessionNum < 0:
        sessionNum = 0
    request.session['sessionNum'] = sessionNum
    return redirect("/playRoundTest/")

def nextRoundPage(request):
    sessionNum = request.session.get('sessionNum', 0)
    sessionNum += 1
    if getPage("ExperimentTest", sessionNum) is not None:
        request.session['sessionNum'] = sessionNum
    return redirect("/playRoundTest/")

def roundTest(request):
    sessionNum = request.session.get('sessionNum', 0)
    if sessionNum == 0:
        return nextRoundPage(request)
    user_id = request.user.id
    page = getPage("ExperimentTest", sessionNum)
    if page is None:
        return HttpResponse("Page " + str(sessionNum) + " does not exist")
    print("PAGE:", page)
    if page is None:
        return HttpResponse("ERROR WITH PAGE" + str(sessionNum))
    pageType = page.content_object
    print("PAGE TYEP", pageType)
    #pageType = "survey" ## Determine this by checking page number to experiment pages
    if isinstance(pageType, AudioRound):
        print("AUDIO ROUND")
        url = settings.MEDIA_URL + str(pageType.audio_ref.file_location)  # getRoundFile()
        context = {
            'page': 'audio',
            'audio': url,
            'sessionNum': sessionNum
        }
        return render(request, 'ExperimentTemplates/standardPage.html', context)
    elif isinstance(pageType, TextRound):
        print("TECT ROD")
       # url = getRoundFile()
        context = {
            'page': 'text',
            'text': pageType.text,
            'sessionNum': sessionNum
        }
        return render(request, 'ExperimentTemplates/standardPage.html', context)
    elif isinstance(pageType, SurveyExample):
        print("SURAV")
        #url = getRoundFile()
        context = {
            'page': 'survey',
            'text': "Please fill this survey",
            'sessionNum': sessionNum,
            'form': AudioForm() 
        }
        return render(request, 'ExperimentTemplates/standardPage.html', context)
    return HttpResponse("Error with experiment")

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

def ajaxTest(request):
    return render(request, 'ajaxTesting.html')


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

def createPostTest(request):
    if request.method == 'POST':
        post_text = request.POST.get('the_post')
        response_data = {}


        response_data['result'] = 'Create post successful!'
        print("DATA SENT")

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

def createTextRound(text, experiment_id):
    experiment = Experiment.objects.filter(title=experiment_id)[0]
    textRound = TextRound(text=text, experiment=experiment)
    textRound.save()
    return textRound


def createTextRound_POST(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        experiment_id = request.POST.get('experiment_id')
        createTextRound(text, experiment_id)
        response_data = {}


        response_data['result'] = 'Create post successful!'

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )



""" import re

string = "@@@OBJECT-START@@@+$name=Paul$END$text=Hello, my welcome to the experiment$END$experimentID=fjea2349jakfe$END]++[word=hi]+@@@OBJECT-START@@@"

splitString = string.split('@@@OBJECT-START@@@')

print(splitString[1])

_, _, a = splitString[1].partition("$name=")
name, _, _ = a.partition("$END")

_, _, a = splitString[1].partition("$text=")
text, _, _ = a.partition("$END")

_, _, a = splitString[1].partition("$experimentID=")
experimentID, _, _ = a.partition("$END")

print(name)
print(text)
print(experimentID)
 """