##from curses.ascii import HT
from email.mime import audio
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import AudioForm, ResearcherSignUpForm, ExperimenteeSignUpForm
from .models import Survey, User, set_file_name, Audio_store, Word, Experiment, Page, SurveyRound, AudioRound, TextRound
from .audio_manipulation import combineAudios, getRoundFile
from .processRoundData import processRound, getVar, createPage, createAudioRound, createSurveyRound, getQuestions, createTextRound, createSurveyQuestion
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
fake_user, fake_experiment = create_Fake_Models()


from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


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
        if form.is_valid(): 
            global fake_user
            user = request.user
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
            print("Word created", associated_word_instance, associated_word_instance.user_source)
            print("Word list", Word.objects.filter(user_source=user))


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
    print("Get page: ", experimentID, pageNumber)
    experiment = Experiment.objects.filter(id=experimentID)[0]
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
    print("next page")
    user_experiment_id = request.session.get('experiment_id', fake_experiment.id)
    print("us ex", user_experiment_id)
    sessionNum = request.session.get('sessionNum', 0)
    sessionNum += 1
    if getPage(user_experiment_id, sessionNum) is not None:
        request.session['sessionNum'] = sessionNum
    return redirect("/playRoundTest/")

def roundTest(request):
    user = request.user
    experiment_id = request.GET.get('id')
    if experiment_id is None:
        experiment_id = fake_experiment.id
    if 'experiment_id' not in request.session:
        print("SETTING KEYS")
        user_experiment_id = request.session.get('experiment_id', experiment_id)
        sessionNum = request.session.get('sessionNum', 0)
        request.session.modified = True
        redirect('/playRoundTest/?id=' + str(experiment_id))
    experiment_id = int(experiment_id)
    user_experiment_id = request.session.get('experiment_id', experiment_id)
    sessionNum = request.session.get('sessionNum', 0)
    request.session.modified = True
    print("ID", user_experiment_id)
    print("ID", request.session['experiment_id'])
    if experiment_id != user_experiment_id and experiment_id != fake_experiment.id:
        request.session['experiment_id'] = experiment_id
        request.session['sessionNum'] = 0
    sessionNum = request.session.get('sessionNum', 0)
    user_experiment_id = request.session['experiment_id']
    if sessionNum == 0:
        return nextRoundPage(request)
    user_id = request.user.id
    page = getPage(user_experiment_id, sessionNum)
    if page is None:
        return HttpResponse("Page " + str(sessionNum) + " does not exist")
    if page is None:
        return HttpResponse("ERROR WITH PAGE" + str(sessionNum))
    pageType = page.content_object
    #pageType = "survey" ## Determine this by checking page number to experiment pages
    if isinstance(pageType, AudioRound):
        print("AUDIO ROUND")
        mumbles = pageType.mumbles
        pairs = pageType.pairs
        placebo = pageType.placebo
        print("sneding user", user)
        url = getRoundFile(mumbles=mumbles, pairs=pairs, placebo=placebo, user=user) #'' #settings.MEDIA_URL + str(pageType.audio_ref.file_location)  # getRoundFile()
        context = {
            'page': 'audio',
            'mumbles': mumbles,
            'pairs': pairs,
            'placebo': placebo,
            'sessionNum': sessionNum,
            'url': url
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
    elif isinstance(pageType, SurveyRound):
        print("SURAV")
        #url = getRoundFile()
        questions = getQuestions(pageType.survey)
        context = {
            'page': 'survey',
            'surveyName': pageType.survey.name,
            'questions': questions,
            'sessionNum': sessionNum
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

def listExperiments(request):
    user_id = request.user.id
    experiments = Experiment.objects.all()
    context = {
        "object_list": experiments
    }
    return render(request, 'listExperiments.html', context)


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
        return redirect("/showAudios/")


    
def logout_view(request):
    logout(request)
    return redirect("/login")

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


def createExperiment(request):
    return render(request, "ResearcherPages/createExperiment.html")


def createExperiment_POST(request):
    if request.method == 'POST':
        global fake_user
        user = fake_user  # request.user
        roundInfo = request.POST.get('roundInfo')

        
        roundInfoSplit = roundInfo.split('@@@OBJECT-DELIM@@@')

        experiment = None

        pageNum = 1
        pages = list()

        for roundObj in roundInfoSplit:
            if roundObj != '':
                round = None
                data = processRound(roundObj)
                if data['roundType'] == "experiment":
                    experimentName = data['experimentName']
                    experiment = Experiment(user_source=user, title=experimentName)
                    experiment.save()

                elif data['roundType'] == "survey":
                    name = data['name']
                    questions = data['questions']

                    survey = Survey(name=name, user_source=user)
                    survey.save()

                    questionNumber = 1

                    for question in questions:
                        questionText = question['questionText']
                        questionType = question['questionType']
                        question = createSurveyQuestion(user, survey, questionText, questionType, questionNumber)
                        questionNumber += 1

                    round = createSurveyRound(experiment, survey, user)

                elif data['roundType'] == "audio":
                    mumbles = bool(data['mumbles'])
                    pairs = int(data['pairs'])
                    placebo = bool(data['placebo'])
                    round = createAudioRound(mumbles, pairs, placebo, experiment, user)
                elif data['roundType'] == "text":
                    text = data['text']
                    round = createTextRound(text, experiment, user)

                if round is not None:
                    new_page = createPage(experiment, pageNum, round, user)
                    pages.append(new_page)
                    pageNum += 1
                else:
                    print("round none")

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
