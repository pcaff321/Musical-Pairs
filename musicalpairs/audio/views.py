##from curses.ascii import HT
from collections import UserDict
from email.mime import audio
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import AudioForm, ResearcherSignUpForm, ExperimenteeSignUpForm, PublishForm
from .models import Survey, User, set_file_name, Audio_store, Word, Experiment, Page, SurveyRound, AudioRound, TextRound, Survey_James
from .audio_manipulation import getRoundFile
from .processRoundData import processRound, getVar, createPage, createAudioRound, createSurveyRound, getQuestions, createTextRound, createSurveyQuestion
from .serializers import Audio_serializer, SurveySerializer, CreateSurveySerializer
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

from django.urls import reverse
from django.core.mail import send_mail
from pyexpat.errors import messages
from audioop import reverse

##JAMES

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def survey_view(request):
    return render(request, 'mainsurvey.html')


@method_decorator(csrf_exempt, name='dispatch')
class SurveyView(generics.ListAPIView):
    queryset = Survey_James.objects.all()
    serializer_class = SurveySerializer

@method_decorator(csrf_exempt, name='dispatch')
class GetRoomView(APIView):
    serializer_class = SurveySerializer
    lookup_url_kwarg = 'code'

    def get(self, request, format=None):
        code = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room = Survey_James.objects.filter(code=code)
            if len(room) > 0:
                data = SurveySerializer(room[0]).data
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'Bad Request': 'Code paramater not found in request'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def getRoundList(request):
    print("HER")     
    user = request.user
    print("not here", user)
    experiments = Experiment.objects.filter(user_source=user)
    print("expeimernts: ", experiments)
    experiment = experiments[0]
    pages = Page.objects.filter(experiment=experiment).order_by('page_number')
    round_list = {}
    roundPageNum = 0
    print("At for loop start")
    for page in pages:
        roundPageNum += 1
        roundContent = list()
        pageType = page.content_object
        if isinstance(pageType, AudioRound):
            mumbles = pageType.mumbles
            pairs = pageType.pairs
            placebo = pageType.placebo
            url = getRoundFile(mumbles=mumbles, pairs=pairs, placebo=placebo, user=user, experiment=experiment, pageModel=page) #'' #settings.MEDIA_URL + str(pageType.audio_ref.file_location)  # getRoundFile()
            roundContent = ["audio", mumbles, pairs, placebo, url]
            round_list[roundPageNum] = roundContent
        elif isinstance(pageType, TextRound):
            roundContent = ["text", "Text Round", pageType.text]
            round_list[roundPageNum] = roundContent
        elif isinstance(pageType, SurveyRound):
            questions = getQuestions(pageType.survey)
            for question in questions:
                roundContent = list()
                questionText = question['questionText']
                questionType = question['questionType']
                if questionType == "slider":
                    questionType = "Slider"
                elif questionType == "text":
                    questionType = "Text"
                elif questionType == "yesOrNo":
                    questionType = "Yes/No"
                roundContent = ["question", questionText, questionType]
                round_list[roundPageNum] = roundContent
                roundPageNum += 1
    print("Round List!", round_list)
    return round_list
    
""" 
@method_decorator(csrf_exempt, name='dispatch')
class CreateSurveyView(APIView):
    print("Top")
    serializer_class = CreateSurveySerializer
    def post(self, request, format="None"):
        print("Post survey")
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            name = serializer.data.get("name")
            round_count = serializer.data.get("round_count")
            round_list = serializer.data.get("round_list")
            host = self.request.session.session_key
            survey = Survey_James(
                host = host,
                name = name,
                round_count = round_count,
                #round_list = {
                #    1: ["text", "Introduction", "Welcome to my study!", "Paragraph 2"],
                #    2: ["audio", True, 1, False, "/static/door_creak.wav"],
                #    3: ["question", "Is my survey based?", "Yes/No"],
                #    4: ["question", "How based?", "Slider"],
                #    5: ["question", "Describe in your own words how based it was", "Text"]
                #}
                round_list = getRoundList(request)
            )
            survey.save()

            return Response(SurveySerializer(survey).data, status=status.HTTP_201_CREATED) """

@method_decorator(csrf_exempt, name='dispatch')
class CreateSurveyView(APIView):
    serializer_class = CreateSurveySerializer
    def post(self, request, format="None"):
        if not self.request.session.exists(self.request.session.session_key):
           self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            name = serializer.data.get("name")
            round_count = serializer.data.get("round_count")
            round_list = serializer.data.get("round_list")
            host = self.request.session.session_key
            survey = Survey_James(
                host = host,
                name = name,
                round_count = round_count,
                round_list = getRoundList(request)
            )
            survey.save()

            return Response(SurveySerializer(survey).data, status=status.HTTP_201_CREATED)


## END

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

            print("AUDIO STORE URL", audio_store_instance.file_location.url)

            # Make associated Word object
            associated_word_instance = Word(word=word, user_source=user, audio_store=audio_store_instance)
            associated_word_instance.save()
            print("Word created", associated_word_instance, associated_word_instance.user_source)
            print("Word list", Word.objects.filter(user_source=user))


            return redirect(showAudios)
    else: 
        form = AudioForm() 
    return render(request, 'aud.html', {'form' : form}) 


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
    sessionInfo = request.session.get('sessionInfo', [fake_experiment.id, 0])
    user_experiment_id = sessionInfo[0]
    sessionNum = sessionInfo[1]
    sessionNum -= 1
    if sessionNum < 0:
        sessionNum = 0
    request.session['sessionInfo'] = [user_experiment_id, sessionNum]
    return redirect('playRoundTest')

def nextRoundPage(request):
    print("next page")
    sessionInfo = request.session.get('sessionInfo', [fake_experiment.id, 0])
    user_experiment_id = sessionInfo[0]
    sessionNum = sessionInfo[1]
    sessionNum += 1
    if getPage(user_experiment_id, sessionNum) is not None:
        request.session['sessionInfo'] = [user_experiment_id, sessionNum]
    return redirect('playRoundTest')


def roundTest(request):
    user = request.user
    experiment_id = request.GET.get('id')
    pageNum = request.GET.get('page')
    if experiment_id is None:
        experiment_id = fake_experiment.id
    if pageNum is None:
        pageNum = 0
    sessionInfo = request.session.get('sessionInfo', [experiment_id, pageNum])
    user_experiment_id = sessionInfo[0]
    sessionNum = sessionInfo[1]
    if experiment_id != user_experiment_id and experiment_id != fake_experiment.id:
        user_experiment_id = experiment_id
        sessionNum = 0
        request.session['sessionInfo'] = [user_experiment_id, sessionNum]
    if int(sessionNum) <= 0:
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
        experiment = pageType.experiment
        print("sneding user", user)
        if len(Word.objects.filter(user_source=user)) < (pairs * 2):
            return prevRoundPage(request)
        url = getRoundFile(mumbles=mumbles, pairs=pairs, placebo=placebo, user=user, experiment=experiment, pageModel=page) #'' #settings.MEDIA_URL + str(pageType.audio_ref.file_location)  # getRoundFile()
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

""" def roundTest(request):
    user = request.user
    experiment_id = request.GET.get('id')
    pageNum = request.GET.get('page')
    if experiment_id is None:
        experiment_id = fake_experiment.id
    experiment_id = int(experiment_id)
    user_experiment_id = request.session.get('experiment_id', experiment_id)
    sessionNum = request.session.get('sessionNum', 0)
    print("SESS", request.session)
    if experiment_id != user_experiment_id and experiment_id != fake_experiment.id:
        request.session['experiment_id'] = experiment_id
        request.session['sessionNum'] = 0
    sessionNum = request.session.get('sessionNum', 0)
    user_experiment_id = request.session.get('experiment_id', experiment_id)
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
        experiment = pageType.experiment
        print("sneding user", user)
        url = getRoundFile(mumbles=mumbles, pairs=pairs, placebo=placebo, user=user, experiment=experiment, pageModel=page) #'' #settings.MEDIA_URL + str(pageType.audio_ref.file_location)  # getRoundFile()
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
    return HttpResponse("Error with experiment") """




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
        return redirect('showAudios')


    
def logout_view(request):
    logout(request)
    return redirect('login')

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
        user = request.user
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



## Craig Stuff

@login_required
@csrf_exempt
def publish(request):
    if request.method=='POST':
        form = PublishForm(request.POST)
        if form.is_valid():
            exp = form.cleaned_data['experiment']
            name = request.user.username
            subject = str(exp) + " update: " + form.cleaned_data['subject']
            body = form.cleaned_data['body']
            emails = []
            message = "Nobody subscribed to this experiment, therefore no message was sent"
            if exp.subscribers.all().count() > 0:
                for user in exp.subscribers.all():
                    emails.append(getattr(user, "email"))
                send_mail(subject, body, "musicalpairs123@gmail.com", emails)
                message = "Message sent successfully"
            form = PublishForm()
            return render(request, 'publish.html', {'form':form, 'message': message})
    else:
        form = PublishForm()
        message = ""
    return render(request, 'publish.html', {'form' : form, 'message': message})


def listExperiments(request):
    if request.method == 'POST':
        user_id = request.user.id
        exp_id = int(request.POST.get('experiment_id'))
        user = User.objects.get(id=user_id)
        exp = Experiment.objects.get(id=exp_id)
        title = str(getattr(exp,"title"))
        message = "You already subscribed to " + title
        if user not in exp.subscribers.all():
            exp.subscribers.add(user)
            message = "Subscription to  " + title + " successful"
        ctx = {"message": message}
        return render(request, "subscribe.html", ctx)
    elif request.method == 'GET':
        name = request.GET.get('search',None)
        experiments = Experiment.objects.all()
        num = Experiment.objects.all().count()
        if name:
            experiments = Experiment.objects.filter(title__contains=name)
            num = Experiment.objects.filter(title__contains=name).count()
        context = {"object_list": experiments, "num":num}
        return render(request, 'listExperiments.html', context)