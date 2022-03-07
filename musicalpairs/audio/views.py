##from curses.ascii import HT
import datetime
from collections import UserDict
import csv
from email.mime import audio
import mimetypes
from msvcrt import getch
from matplotlib.pyplot import isinteractive
from pydub import AudioSegment
from msilib import datasizemask
import os
from pickle import FALSE
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from numpy import round_
from .forms import AudioForm, CustomAuthenticationForm, ResearcherSignUpForm, ExperimenteeSignUpForm, PublishForm, PublishForm2
from .models import ImageRound, Survey, SurveyAnswer, SurveyQuestion, User, WordBundle, set_file_name, Audio_store, Word, Experiment, Page, SurveyRound, AudioRound,\
    TextRound, Survey_James, UserWordRound, UserPairGuess, UserUniqueExperiment, ExperimentUpdate, AssociatedSurvey
from .audio_manipulation import getRoundFile
from .processRoundData import createImageRound, processRound, getVar, createPage, createAudioRound, createSurveyRound, getQuestions, createTextRound, createSurveyQuestion
from .serializers import Audio_serializer, SurveySerializer, CreateSurveySerializer
from rest_framework.renderers import JSONRenderer
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.db import models
import json
import re
import math
import string
from django.core.files.base import ContentFile
import pandas as pd
from datetime import datetime, date, timedelta

from .makeFakeModels import create_Fake_Models, makeMumbleWords, makePietroWords, replicateMusicalPairs


try:
    print("CALLING CREATE FAKE MODELS")
    fake_user, fake_experiment = create_Fake_Models()
    makePietroWords()
    makeMumbleWords()
    replicateMusicalPairs()
except:
    print("DB not migrated yet")


from django.template.defaulttags import register

from django.urls import reverse
from django.core.mail import send_mail
from pyexpat.errors import messages

def processPageInfo(page):
    pageType = page.content_object
    if isinstance(pageType, AudioRound):
        pairs = pageType.pairs
        prime = pageType.prime
        roundContent = {"pageType":"audio",
         "pairs":pairs,
          "prime": prime,
          "bundle_id": pageType.word_bundle.id
          }
    elif isinstance(pageType, TextRound):
        roundContent = {"pageType":"text", "text": pageType.text, "title": pageType.title}
    elif isinstance(pageType, ImageRound):
        question = SurveyQuestion.objects.filter(survey=pageType.survey)[0].questionText
        questionType = SurveyQuestion.objects.filter(survey=pageType.survey)[0].questionType
        roundContent = {"pageType":"image", "url": pageType.image.url, 
        "questionText": question, "questionType": questionType, "title": pageType.name}
    elif isinstance(pageType, SurveyRound):
        questions = getQuestions(pageType.survey)
        questionList = list()
        for question in questions:
            roundContent = list()
            questionText = question['questionText']
            questionType = question['questionType']
            if questionType == "text":
                questionType = "Text"
            elif questionType == "slider":
                questionType = "Slider"
            elif questionType == "yesOrNo":
                questionType = "Yes/No"
            elif questionType == "Agree":
                questionType = "Agree"
            questionInfo = {"questionText":questionText, "questionType":questionType}
            questionList.append(questionInfo)
        roundContent = {"pageType": "survey", "questionList": questionList}
    return roundContent

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

def getResultsByRound(wordRound):
    user_pair_guesses = list(UserPairGuess.objects.filter(associated_word_round=wordRound))

    guesses_as_dicts = list()

    score = 0
    amount = len(user_pair_guesses)


    for pair in user_pair_guesses:
        word1 = str(pair.pair.audio1.word)
        word2 = str(pair.pair.audio2.word)
        answer = str(pair.answer)
        placebo = bool(pair.placebo_added)
        pair_dict = {
            "word1": word1,
            "word2": word2,
            "answer": answer,
            "placebo": placebo,
            "pair_guess_id": pair.id
        }
        if word2.lower() == answer.lower():
            score += 1
        guesses_as_dicts.append(pair_dict)
    
    return guesses_as_dicts, score, amount

def getWordBundle(user):
    userBundle = WordBundle.objects.filter(user_source=user)
    if userBundle.exists():
        userBundle = userBundle[0]
    else:
        userBundle = WordBundle(name="Your Audios", public=False, user_source=user)
        userBundle.save()
    return userBundle

def createPath(path):

    isExist = os.path.exists(path)

    if not isExist:
        print("DOESN'T EXIST")
        os.makedirs(path)

def getAnswersFromSurveyForUser(survey, user):
    answerList = list()
    questions = getQuestions(survey)

    for question in questions:
        surveyQuestion = SurveyQuestion.objects.filter(id=question['id'])[0]
        answers = SurveyAnswer.objects.filter(surveyQuestion=surveyQuestion, user_source=user)
        answerList = list()
        for answer in answers:
            question['answer'] = answer.answer

    surveyInfo = {'survey': survey.id,
             'questions': questions   
    }

    return surveyInfo

def getResultsForUser(user, experiment):
    pages = Page.objects.filter(experiment=experiment).order_by('page_number')
    pages = list(pages)
    pagesList = list()
    imageRounds = list()
    surveyRounds = list()
    for page in pages:
        if isinstance(page.content_object, AudioRound):
            pagesList.append(page)
        elif isinstance(page.content_object, ImageRound):
            imageRounds.append(page.content_object)
        elif isinstance(page.content_object, SurveyRound):
            surveyRounds.append(page.content_object)

    wordRounds = list()
    for page in pagesList:
        pageType = page.content_object
        if isinstance(pageType, AudioRound):
            wordRound = UserWordRound.objects.filter(associated_audio_round=pageType, for_user=user)
            if wordRound.exists():
                wordRounds.append(wordRound[0])
            else:
                print("WORD ROUND NONE")
    
    roundLists = list()
    roundNum = 1
    for round in wordRounds:
        pairInfo, score, amount = getResultsByRound(round)
        roundInfo = {
            "name": "Audio Round " + str(roundNum),
            "type": "audio",
            "score": score,
            "amount": amount,
            "pairsList": pairInfo
        }
        roundLists.append(roundInfo)
        roundNum += 1

    roundNum = 1
    for imageR in imageRounds:
        survey = imageR.survey
        surveyInfo = getAnswersFromSurveyForUser(survey, user)
        roundInfo = {
            "type": "image",
            "url": imageR.image.url,
            "name": "Image Round " + str(roundNum),
            "surveyInfo": surveyInfo
        }
        roundNum += 1
        roundLists.append(roundInfo)


    roundNum = 1
    for surveyR in surveyRounds:
        survey = surveyR.survey
        surveyInfo = getAnswersFromSurveyForUser(survey, user)
        roundInfo = {
            "type": "image",
            "name": "Survey Round " + str(roundNum),
            "surveyInfo": surveyInfo
        }
        roundNum += 1
        roundLists.append(roundInfo)

    
    return roundLists


@login_required
def home(request):
    return render(request, 'home.html')

def index(request):
    return render(request, 'index.html')


def getTrimmedAudio(user_id, url=False):
    if url:
        return os.path.join(settings.MEDIA_URL, str(user_id), "trimmedSounds", "trimmedAudio.wav").replace("\\","/")
    return os.path.join(settings.MEDIA_ROOT, str(user_id), "trimmedSounds", "trimmedAudio.wav").replace("\\","/")



@csrf_exempt
def getRoundList(request):
    user = request.user
    experiment_id = request.GET.get("id", None)
    if experiment_id is None:
        return ["text", "Invalid Experiment", "Please Check if experimetn ID is correct"]
    experiments = Experiment.objects.filter(id=experiment_id)
    if not experiments.exists():
        return ["text", "Invalid Experiment", "Please Check if experimetn ID is correct"]
    experiment = experiments[0]
    experiment_id = request.GET.get('id', None)
    if experiment_id is not None:
        experiment_Check = Experiment.objects.filter(id=experiment_id)
        if experiment_Check.exists():
            experiment = experiment_Check[0]
    pages = Page.objects.filter(experiment=experiment).order_by('page_number')
    round_list = {}
    roundPageNum = 1
    for page in pages:
        roundContent = list()
        pageType = page.content_object
        if isinstance(pageType, AudioRound):
            mumbles = False
            pairs = pageType.pairs
            placebo = False
            roundFiles = getRoundFile(mumbles=mumbles, pairs=pairs, placebo=placebo, user=user, experiment=experiment, pageModel=page) #'' #settings.MEDIA_URL + str(pageType.audio_ref.file_location)  # getRoundFile()
            url = roundFiles[0].audio_ref.file_location.url
            roundContent = ["audio", mumbles, pairs, placebo, url]
            round_list[roundPageNum] = roundContent
            roundPageNum += 1

            roundContent = ["text", "Now Listen To The Following Audios", "Answer the questions that proceed each audio. Your goal is to remember the second word to a pair"]
            round_list[roundPageNum] = roundContent
            roundPageNum += 1
            

            #add pair guesses
            guess = 0
            halfWayPoint = math.floor((len(roundFiles) - 1) / 2 )
            for pairGuess in roundFiles:
                if guess == 0:
                    guess += 1
                else:

                    url = pairGuess.audio_ref.file_location.url
                    roundContent = ["audio", mumbles, pairs, placebo, url]
                    round_list[roundPageNum] = roundContent
                    roundPageNum += 1

                    question_id = pairGuess.id
                    roundContent = ["question", "What was the second word?", "Text", question_id, experiment_id, "pair"]
                    round_list[roundPageNum] = roundContent
                    roundPageNum += 1

                    if guess == halfWayPoint:	
                        user_source = experiment.user_source	
                        question_id = 0	
                        halfWaySurvey = Survey.objects.filter(name=str(pageType.id), user_source=experiment.user_source)	
                        if halfWaySurvey.exists():	
                            halfWaySurvey = halfWaySurvey[0]	
                        else:	
                            halfWaySurvey = Survey(name=str(pageType.id), user_source=user_source)	
                            halfWaySurvey.save()	
                        questionText = "How are you finding this round so far?"	
                        surveyQuestion = SurveyQuestion.objects.filter(user_source=user_source, survey=halfWaySurvey, questionText=questionText)	
                        if surveyQuestion.exists():	
                            surveyQuestion = surveyQuestion	
                        else:	
                            surveyQuestion = createSurveyQuestion(user_source, halfWaySurvey, questionText, 2, 1)	
                        associatedSurvey = AssociatedSurvey.objects.filter(survey=halfWaySurvey)	
                        if associatedSurvey.exists():	
                            associatedSurvey = associatedSurvey[0]	
                        else:	
                            associatedSurvey = AssociatedSurvey(survey=halfWaySurvey, content_object=pageType)	
                            associatedSurvey.save()	
                        question_id = surveyQuestion.id
                        roundContent = ["question", questionText, "Slider", question_id, experiment_id, "question"]	
                        round_list[roundPageNum] = roundContent	
                        roundPageNum += 1	
                    guess += 1
            """ roundContent = ["text", "The following questions concern the round you just completed",
             "Please answer the following questions honestly to best gauge your experience."]

            roundContent = ["question", "During this round, I was interrupted", "Slider", 0]
            round_list[roundPageNum] = roundContent
            roundPageNum += 1

            roundContent = ["question", "During this round, I put forward my best effort", "Slider", 0]
            round_list[roundPageNum] = roundContent
            roundPageNum += 1

            roundContent = ["question", 
            "During this round, some noises around me made it harder for me to understand the words", 
            "Slider", 0]
            round_list[roundPageNum] = roundContent
            roundPageNum += 1

            roundContent = ["question", 
            "During this round, I felt tired", 
            "Slider", 0]
            round_list[roundPageNum] = roundContent
            roundPageNum += 1 """


        elif isinstance(pageType, ImageRound):
            image = pageType.image.url
            roundContent = ["image", image]
            round_list[roundPageNum] = roundContent
            roundPageNum += 1

            question = getQuestions(pageType.survey)[0]
            roundContent = list()
            questionText = question['questionText']
            questionType = question['questionType']
            if questionType == "slider":
                questionType = "Slider"
            elif questionType == "text":
                questionType = "Text"
            elif questionType == "yesOrNo":
                questionType = "Yes/No"
            elif questionType == "Agree":
                questionType = "Agree"
            roundContent = ["question", questionText, questionType, question['id'], experiment_id, "question"]
            round_list[roundPageNum] = roundContent
            roundPageNum += 1




        elif isinstance(pageType, TextRound):
            roundContent = ["text", pageType.title, pageType.text]
            round_list[roundPageNum] = roundContent
            roundPageNum += 1
        # elif isinstance(pageType, ImageRound):
        #     roundContent = ["image", pageType.image.url]
        #     round_list[roundPageNum] = roundContent
        #     roundPageNum += 1

        #     question = getQuestions(pageType.survey)[0]
        #     questionText = question['questionText']
        #     questionType = question['questionType']
        #     roundContent = ["question", questionText, questionType, question['id'], experiment_id, "question"]
        #     round_list[roundPageNum] = roundContent
        #     roundPageNum += 1

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
                elif questionType == "Agree":
                    questionType = "Agree"
                roundContent = ["question", questionText, questionType, question['id'], experiment_id, "question"]
                round_list[roundPageNum] = roundContent
                roundPageNum += 1
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
            user = request.user
            #serializer.data.get("round_count")
            experiments = Experiment.objects.all()
            experiment = experiments[0]
            experiment_id = request.GET.get('id', None)
            if experiment_id is not None:
                experiment_Check = Experiment.objects.filter(id=experiment_id)
                if experiment_Check.exists():
                    experiment = experiment_Check[0]
            name = experiment.title
            round_list = getRoundList(request)
            round_count = len(round_list)
            host = self.request.session.session_key
            survey = Survey_James(
                host = host,
                name = name,
                round_count = round_count,
                round_list = round_list
            )
            survey.save()

            return Response(SurveySerializer(survey).data, status=status.HTTP_201_CREATED)


## END

def createExpTask(request, user, experiment, experiment_id):

    name = experiment.title
    round_list = getRoundList(request)
    round_count = len(round_list)
    host = request.session.session_key
    survey = Survey_James(
        host = host,
        name = name,
        round_count = round_count,
        round_list = round_list
    )
    survey.save()
    userUniqueExperiment = UserUniqueExperiment(for_user=user, experiment=experiment, survey_james=survey)
    userUniqueExperiment.save()


def createExperimentPage(request):
    user = request.user
    userBundle = getWordBundle(user)
    experiments = Experiment.objects.all()
    experiment = experiments[0]
    experiment_id = request.GET.get('id', None)
    if experiment_id is not None:
        experiment_Check = Experiment.objects.filter(id=experiment_id)
        if experiment_Check.exists():
            experiment = experiment_Check[0]

    userUniqueExperiment = UserUniqueExperiment.objects.filter(for_user=user, experiment=experiment)
    if len(userUniqueExperiment) <= 0:
        createExpTask(request, user, experiment, experiment_id)
    return HttpResponse("Request received")


def experimentLoad(request):
    user = request.user
    userBundle = getWordBundle(user)
    experiments = Experiment.objects.all()
    experiment = experiments[0]
    experiment_id = request.GET.get('id', None)
    if experiment_id is not None:
        experiment_Check = Experiment.objects.filter(id=experiment_id)
        if experiment_Check.exists():
            experiment = experiment_Check[0]

    userUniqueExperiment = UserUniqueExperiment.objects.filter(for_user=user, experiment=experiment)
    if len(userUniqueExperiment) > 0:
        return redirect(reverse('surveyPage', kwargs={'roomCode':userUniqueExperiment[0].survey_james.code}))

    return render(request, "experimentLoadingPage.html", {"id": experiment_id})


def checkReady(request):
    user = request.user
    userBundle = getWordBundle(user)
    experiments = Experiment.objects.all()
    experiment = experiments[0]
    experiment_id = request.GET.get('id', None)
    if experiment_id is not None:
        experiment_Check = Experiment.objects.filter(id=experiment_id)
        if experiment_Check.exists():
            experiment = experiment_Check[0]

    userUniqueExperiment = UserUniqueExperiment.objects.filter(for_user=user, experiment=experiment)
    ready = False
    if len(userUniqueExperiment) > 0:
        ready = True

    return JsonResponse({"ready": ready})

    



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
        if form.is_valid(): 
            global fake_user
            user = request.user
            word = form.cleaned_data['word']
            audio_name = "{}_{}".format(request.user.id, word)
            audio_file = form.cleaned_data['file']

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
    trimmedUrl = str(getTrimmedAudio(request.user.id, url=True))
    return render(request, 'aud.html', {'form' : form, 'trimmedUrl': trimmedUrl}) 


@login_required
def playAudioFile(request):
    user_id = request.user.id
    url = settings.MEDIA_URL + "user_{}/{}.wav".format(user_id, "lalala")
    return render(request, 'playAudio.html', {'link': url })

def getPage(experimentID, pageNumber):
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
        mumbles = pageType.mumbles
        pairs = pageType.pairs
        placebo = pageType.placebo
        experiment = pageType.experiment
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
       # url = getRoundFile()
        context = {
            'page': 'text',
            'text': pageType.text,
            'sessionNum': sessionNum
        }
        return render(request, 'ExperimentTemplates/standardPage.html', context)
    elif isinstance(pageType, SurveyRound):
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
    audios_of_user = Word.objects.filter(user_source=request.user)
    for instance in audios_of_user:
        instance.audio_store.file_location = settings.MEDIA_URL + str(instance.audio_store.file_location)
    no_audios = True
    if len(audios_of_user) > 0:
        no_audios = False
    context = {
        "object_list": audios_of_user,
        "no_audios": no_audios
    }
    return render(request, 'showAudios.html', context)

@login_required
def myExperiments(request):
    user_id = request.user.id
    experiments = Experiment.objects.filter(user_source=request.user)
    for exp in experiments:
        participants = len(UserUniqueExperiment.objects.filter(experiment=exp))
        exp.participants = participants
    no_exp = True
    if len(experiments) > 0:
        no_exp = False
    context = {
        "object_list": experiments,
        "no_exp": no_exp
    }
    return render(request, 'myExperiments.html', context)

@login_required
def takenExperiments(request):
    user = request.user
    exps = UserUniqueExperiment.objects.filter(for_user=user)
    print("exp", exps)
    user_id = user.id
    experiments = list()
    for exp in exps:
        experiments.append(exp.experiment)
    no_exp = True
    if len(experiments) > 0:
        no_exp = False
    context = {
        "object_list": experiments,
        "no_exp": no_exp
    }
    return render(request, 'experimentsTaken.html', context)


def publicExperiments(request):
    print("CALLING CREATE FAKE MODELS")
    fake_user, fake_experiment = create_Fake_Models()
    makePietroWords()
    makeMumbleWords()
    replicateMusicalPairs()
    experiments = Experiment.objects.filter(public=True)
    for exp in experiments:
        participants = len(UserUniqueExperiment.objects.filter(experiment=exp))
        exp.participants = participants
    no_exp = True
    if len(experiments) > 0:
        no_exp = False
    context = {
        "object_list": experiments,
        "no_exp": no_exp
    }
    return render(request, 'publicExperiments.html', context)

def getQuestionsForExperiment(experiment):
    
    surveyRounds = SurveyRound.objects.filter(experiment=experiment).order_by('id')
    surveys = list()
    for surveyRound in surveyRounds:
        survey = surveyRound.survey
        questions = getQuestions(survey)

        for question in questions:
            surveyQuestion = SurveyQuestion.objects.filter(id=question['id'])[0]
            answers = SurveyAnswer.objects.filter(surveyQuestion=surveyQuestion)
            answerList = list()
            for answer in answers:
                answerDict = {
                    'user_id': answer.user_source.id,
                    'answer': answer.answer
                }
                answerList.append(answerDict)
            question['answers'] = answerList
        

        surveys.append(
            {'survey': survey.id,
             'questions': questions   
        })

        return surveys

def getAnswersFromSurvey(survey):
    answerList = list()
    questions = getQuestions(survey)

    for question in questions:
        surveyQuestion = SurveyQuestion.objects.filter(id=question['id'])[0]
        answers = SurveyAnswer.objects.filter(surveyQuestion=surveyQuestion)
        answerList = list()
        for answer in answers:
            answerDict = {
                'user_id': answer.user_source.id,
                'answer': answer.answer
            }
            answerList.append(answerDict)
        question['answers'] = answerList

    surveyInfo = {'survey': survey.id,
             'questions': questions   
    }

    return surveyInfo

def processPageInfoForQuestions(page):
    pageType = page.content_object
    roundContent = None
    if isinstance(pageType, SurveyRound):
        survey = pageType.survey
        roundContent = {
            'type': 'survey',
            'surveyInfo': getAnswersFromSurvey(survey)
        }
    elif isinstance(pageType, ImageRound):
        survey = pageType.survey
        url = None
        questionInfo = getAnswersFromSurvey(survey)
        question = questionInfo['questions'][0]['questionText']
        questionType = questionInfo['questions'][0]['questionType']
        id = questionInfo['questions'][0]['id']
        answers = questionInfo['questions'][0]['answers']
        roundContent = {
            'type': 'image',
            'title': pageType.name,
            'url': pageType.image.url,
            'questionText': question,
            'questionType': questionType,
            'id': id,
            'answers': answers,
            'bar_chart': False
        }
    if roundContent:
        roundContent['id'] = pageType.id
    
    return roundContent


def getExperimentQuestionInfo(experiment):
    pages = Page.objects.filter(experiment=experiment).order_by('page_number')
    pagesList = list()
    for page in pages:
        if isinstance(page.content_object, ImageRound) or isinstance(page.content_object, SurveyRound):
            pagesList.append(processPageInfoForQuestions(page))

    survey = 1
    image = 1
    pageNum = 0
    for page in pagesList:
        page['num'] = pageNum
        pageNum += 1
        if page['type'] == "survey":
            page['roundName'] = "Survey Round " + str(survey)
            survey += 1
        elif page['type'] == "image":
            page['roundName'] = "Image Round " + str(image)
            image += 1
        
    
    return pagesList


def convertToBarChartData(roundInfo):
    labels = list(range(0,11))
    questionType = roundInfo['questionType']
    if questionType == "Agree":
        labels = list(range(1,6))
    elif questionType == "yesOrNo":
        labels = ["Yes", "No"]
    data = list(0 for i in range(len(labels)))
    if questionType == "slider":
        for answer in roundInfo['answers']:
            answer = int(answer['answer'])
            if answer >=  0 and answer < len(labels):
                data[answer] += 1
    elif questionType == "yesOrNo":
        for answer in roundInfo['answers']:
            answer = 0 if (answer['answer'] == "Yes") else 1
            if answer >=  0 and answer < len(labels):
                data[answer] += 1
    else:
        for answer in roundInfo['answers']:
            answer = int(answer['answer']) - 1
            if answer >=  0 and answer < len(labels):
                data[answer] += 1
    return {"labels": labels, "data": data}


"""        roundContent = {
            'type': 'image',
            'title': pageType.name,
            'url': pageType.image.url,
            'questionText': question,
            'questionType': questionType,
            'answers': answers
        }
    if roundContent:
        roundContent['id'] = pageType.id
    
    return roundContent
 """

def makeChartData(pages):
    new_pages = pages
    for page in new_pages:
        if page['type'] == "image":
            questionType = page['questionType']
            if questionType == "slider" or questionType == "Agree" or questionType == "yesOrNo":
                page['bar_data'] = convertToBarChartData(page)
                page['bar_data']['title'] = page['questionText']
                page['bar_chart'] = True
                page['id'] = "Chart" + str(page['id'])
                page['Chart_id'] = "TheChart" + str(page['id'])
        if page['type'] == "survey":
            for quest in page['surveyInfo']['questions']:
                questionType = quest['questionType']
                if questionType == "slider" or questionType == "Agree" or questionType == "yesOrNo":
                    quest['bar_data'] = convertToBarChartData(quest)
                    quest['bar_data']['title'] = quest['questionText']
                    quest['bar_chart'] = True
                    quest['id'] = "Chart" + str(quest['id'])




    return new_pages
    

def testingBarCharts(request):
    experimentID = request.GET.get('id', None)
    if experimentID is None:
        return HttpResponse("No ID given")
    experiment = Experiment.objects.filter(id=experimentID)[0]
    info = getExperimentQuestionInfo(experiment)
    context = {
        "pages_list": makeChartData(info)
    }


    return render(request, "ResearcherPages/testingBarCharts.html", context)



def showAnswers(request):
    user_id = request.user.id
    experimentID = request.GET.get('id', None)
    if experimentID is None:
        return HttpResponse("No ID given")
    experiment = Experiment.objects.filter(id=experimentID)
    if experiment.exists():
        experiment = experiment[0]
    else:
        return HttpResponse("Experiment does not exist with given ID")
    surveys = getQuestionsForExperiment(experiment)
    context = {
        "experiment_title": experiment,
        "creator": experiment.user_source.full_name(),
        "email": experiment.user_source.email,
        "surveys": surveys
    }
    return render(request, 'showAnswers.html', context)


def loginView(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    form = CustomAuthenticationForm()
    return render(request, 'login.html', {"form": form})

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
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')


class researcher_signup(CreateView):
    model = User
    form_class = ResearcherSignUpForm
    template_name = 'signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'researcher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')


    
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
        title = request.POST.get('text')
        text = request.POST.get('text')
        experiment_id = request.POST.get('experiment_id')
        createTextRound(title, text, experiment_id)
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
    user = request.user
    listOfBundles = list()
    userBundle = getWordBundle(user)
    listOfBundles.append(userBundle)
    otherBundles = WordBundle.objects.filter(public=True)
    
    for bundle in otherBundles:
        listOfBundles.append(bundle)
    context = {
        "listOfBundles": listOfBundles
    }
    return render(request, "ResearcherPages/createExperiment.html", context)

def errorCheck(roundInfoSplit):
    return True, 'Poop'

def createExperiment_POST(request):
    if request.method == 'POST':
        global fake_user
        user = request.user
        roundInfo = request.POST.get('roundInfo')
        files = None
        imageNumber = 0

        if request.FILES is not None and 'images[]' in dict(request.FILES):
            files = dict(request.FILES)['images[]']

        imageList = []

        if files is not None:
            for image in files:
                imageList.append(image)

        
        roundInfoSplit = roundInfo.split('@@@OBJECT-DELIM@@@')

        experiment = None

        pageNum = 1
        pages = list()
        error = False
        error_msg = ""

        audio_round = 0

        for roundObj in roundInfoSplit:
            if roundObj != '':
                round = None
                data = processRound(roundObj)
                if data['roundType'] == "experiment":
                    experimentName = data['experimentName']
                    if experimentName == "":
                            error = True
                            error_msg = "Experiment Name is blank"
                            break
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
                        if questionText == "":
                            error = True
                            error_msg = "Question is blank"
                            break
                        question = createSurveyQuestion(user, survey, questionText, questionType, questionNumber)
                        questionNumber += 1

                    round = createSurveyRound(experiment, survey, user)

                elif data['roundType'] == "audio":
                    audio_round += 1
                    prime = str(data['prime'])
                    pairs = int(data['pairs'])
                    bundleId = data['bundleID']
                    wordBundle = WordBundle.objects.filter(id=bundleId)
                    if wordBundle.exists():
                        wordBundle = wordBundle[0]
                    else:
                        wordBundle = getWordBundle(user)
                    round = createAudioRound(pairs, prime, experiment, user, wordBundle)
                    wordBundleAmount = len(Word.objects.filter(user_source=wordBundle.user_source))
                    if (wordBundleAmount <= (pairs * 2)):
                        error = True
                        error_msg = "Not enough audios in the word bundle in Audio Round {} to make {} pairs".format(audio_round, pairs)
                        break
                elif data['roundType'] == "text":
                    title = data['title']
                    text = data['text']
                    if title == "":
                            error = True
                            error_msg = "Text round title is blank"
                            break
                    if text == "":
                            error = True
                            error_msg = "Text round text is blank"
                            break
                    round = createTextRound(title, text, experiment, user)
                elif data['roundType'] == "image":
                    if len(imageList) <= imageNumber:
                            error = True
                            error_msg = "Image file is blank"
                            break
                    image = imageList[imageNumber]
                    name = data['name']
                    questionText = data['questionText']
                    if questionText == "":
                            error = True
                            error_msg = "Question is blank in image round"
                            break
                    questionType = data['questionType']
                    if questionType == "input":
                        questionType = 1
                    elif questionType == "slider":
                        questionType = 2
                    elif questionType == "yesOrNo":
                        questionType = 3
                    elif questionType == "Agree":
                        questionType = 4

                    round = createImageRound(image, experiment, user, questionText, questionType, name)
                    imageNumber += 1


                if round is not None:
                    new_page = createPage(experiment, pageNum, round, user)
                    pages.append(new_page)
                    pageNum += 1
                else:
                    print("round none")

        response_data = {}

        if error:
            response_data['result'] = 'Error creating experiment'
            response_data['id'] = experiment.id
            response_data['okay'] = False
            response_data['error_msg'] = error_msg
            experiment.delete()

            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
        )




        response_data['result'] = 'Create post successful!'
        response_data['id'] = experiment.id
        response_data['okay'] = True

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

def editExperiment(request):
    experimentID= request.GET.get('id', None)
    print("ID", experimentID)
    if experimentID is not None:
        experiment = Experiment.objects.filter(id=experimentID)
        if experiment.exists():
            experiment = experiment[0]
            pages = Page.objects.filter(experiment=experiment).order_by('page_number')
            pagesList = list()
            for page in pages:
                pagesList.append(processPageInfo(page))

            user = request.user
            listOfBundles = list()
            userBundle = getWordBundle(user)
            listOfBundles.append(userBundle)
            otherBundles = WordBundle.objects.filter(public=True)
            
            for bundle in otherBundles:
                listOfBundles.append(bundle)

            context = {"experimentName":experiment.title, "experimentList": pagesList, "listOfBundles": listOfBundles}
            return render(request, 'ResearcherPages/editExperiment.html', context)
            
    return HttpResponse("ID not found")


def answerQuestion_POST(request):
    if request.method == 'POST':
        global fake_user
        user = request.user
        questionInfo = request.POST.get('pair_or_question', 'question')
        experiment_ID = request.POST.get('experimentID', None)
        database_ID = request.POST.get('questionID', None)
        answer = request.POST.get('answerValue', "NOT_ANSWERED")
        if database_ID is None:
            return HttpResponse(
            json.dumps({"Error": "no ID given"}),
            content_type="application/json"
            )

        if questionInfo == "question":
            if experiment_ID is None:
                return HttpResponse(
                json.dumps({"Error": "no experiment ID given"}),
                content_type="application/json"
                )
            print("Question Post")
            surveyQuestion = SurveyQuestion.objects.get(id=database_ID)
            experiment = Experiment.objects.get(id=experiment_ID)
            question = SurveyAnswer.objects.filter(user_source=user, surveyQuestion=surveyQuestion)
            if question.exists():
                if not (str(answer) == "NOT_ANSWERED"):
                    question = question[0]
                    question.answer = str(answer)
            else:
                question = SurveyAnswer(surveyQuestion=surveyQuestion, experiment=experiment, user_source=user, answer=str(answer))
            print("ANSWER POST", answer)
            print("Answer", question.answer)
            question.save()
        elif questionInfo == "pair":
            print("Pair Guess")
            if not (str(answer) == "NOT_ANSWERED"):
                pairGuess = UserPairGuess.objects.get(id=database_ID)
                pairGuess.answer = str(answer)
                pairGuess.save()
        else:
            return HttpResponse(
            json.dumps({"Error": "question Type not recognised"}),
            content_type="application/json"
        )

        
        response_data = dict()

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


def showResults(request):
    if request.method == 'GET':
        user = request.user
        experiment_id = request.GET.get('id', None)
        experiment = None
        if experiment_id is not None:
            experiment = Experiment.objects.filter(id=experiment_id)[0]
        else:
            experiment = Experiment.objects.filter(user_source=user)[0]
        roundInfo = getResultsForUser(user, experiment)
        context = {"object_list": roundInfo}
        print("CONTEXT", roundInfo)
        return render(request, 'showResults.html', context)



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
        num = experiments.count()
        if name:
            experiments = Experiment.objects.filter(title__contains=name)
            num = experiments.count()
        context = {"user_id":request.user.id,
        "object_list": experiments, 
        "num":num}
        return render(request, 'listExperiments.html', context)

def getRoundLength(experiment):
    return 10

def viewExperiment_Researcher(request):
    if request.method == 'POST':
        experiment_id = request.POST['experiment_id']
        experiment = Experiment.objects.filter(id=experiment_id)
        exp = experiment[0]
        form = PublishForm2(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            update = ExperimentUpdate(experiment=exp, subject=subject, body=body)
            name = request.user.username
            subject = str(exp) + " update: " + subject
            body = form.cleaned_data['body']
            emails = []
            if exp.subscribers.all().count() > 0:
                for user in exp.subscribers.all():
                    emails.append(getattr(user, "email"))
                send_mail(subject, body, "musicalpairs123@gmail.com", emails)
                update.save()
                return JsonResponse({'success' : True, 'subject': subject, 'body':body})
            else:
                return JsonResponse({'oops':"Nobody subscribed to this experiment, therefore no message was sent."})

        else:
            data ={'error':form.errors}
            return JsonResponse(data)

    else:
        experiment_id = request.GET.get('id')
        experiment = Experiment.objects.filter(id=experiment_id)
        today = datetime.now().date()
        d1 = today - timedelta(1)
        d2 = today - timedelta(2)
        d3 = today - timedelta(3)
        d4 = today - timedelta(4)
        d5 = today - timedelta(5)
        d6 = today - timedelta(6)
        t = UserUniqueExperiment.objects.filter(experiment__in=experiment, created_at__contains=today).count()
        d1 = UserUniqueExperiment.objects.filter(experiment__in=experiment, created_at__contains=d1).count()
        d2 = UserUniqueExperiment.objects.filter(experiment__in=experiment, created_at__contains=d2).count()
        d3 = UserUniqueExperiment.objects.filter(experiment__in=experiment, created_at__contains=d3).count()
        d4 = UserUniqueExperiment.objects.filter(experiment__in=experiment, created_at__contains=d4).count()
        d5 = UserUniqueExperiment.objects.filter(experiment__in=experiment, created_at__contains=d5).count()
        d6 = UserUniqueExperiment.objects.filter(experiment__in=experiment, created_at__contains=d6).count()
        uniquevists = [t, d1, d2, d3, d4, d5, d6]
        uv = json.dumps(uniquevists)
        if not experiment.exists():
            return HttpResponse("ID not recognised")
        form = PublishForm2(initial={'experiment':experiment})
        experiment = experiment[0]
        updates = ExperimentUpdate.objects.filter(experiment=experiment).order_by('-dateSent')
        updates_exist = False
        if updates.exists():
            updates[0]
            updates_exist = True
        else:
            updates = {1: {'subject' : '', 'body' : '', 'dateSent': ''}}
        participants = UserUniqueExperiment.objects.filter(experiment=experiment)
        roundCount = getRoundLength(experiment)
        subscriber_count = experiment.subscribers.count()
        #completed_participants = UserUniqueExperiment.objects.filter(experiment=experiment, page_num=roundCount)
        pages = Page.objects.filter(experiment=experiment).order_by('page_number')
        pagesList = list()
        audio_rounds_exist = False
        for page in pages:
            if isinstance(page.content_object, AudioRound):
                audio_rounds_exist = True
                print("THEY EXIST")
            pagesList.append(processPageInfo(page))

        

        context = {
            "experimentName": experiment.title,
            "id": experiment_id, 
            "participant_count": len(participants),
            #"completed_count": len(completed_participants),
            "form" : form,
            "updates" : updates,
            'updates_exist': updates_exist,
            'subscriber_count': subscriber_count,
            "chartsData": getChartDataContext(request),
            'pages_list': getExperimentQuestionInfo(experiment),
            "experimentList": pagesList,
            "uv": uv,
            'pages_list': makeChartData(getExperimentQuestionInfo(experiment)),
            "experimentList": pagesList,
            "audio_rounds": audio_rounds_exist
        }

        return render(request, "ResearcherPages/viewExperimentInfo.html", context)


def getGuessesBasedOnPrime(experiment, prime):
    pairGuessesQuery = UserPairGuess.objects.filter(prime=prime)
    pairGuesses = list()
    for guess in pairGuessesQuery:
        if guess.associated_word_round.experiment == experiment:
            pairGuesses.append(guess)
    return pairGuesses


def getChartData(guesses):
    correct = 0
    total = len(guesses)
    for guess in guesses:
        pair = guess.pair
        word1 = pair.audio1.word
        word2 = pair.audio2.word
        answer = guess.answer
        if word2.lower() == answer.lower():
            correct += 1
    scoresData = [correct, (total-correct)]
    labels = ["Correct", "Incorrect"]
    percent = 0.0
    if total > 0:
        percent = round((correct / total) * 100, 2)

    return scoresData, labels, percent


def getChartDataContext(request):
    experiment_id = request.GET.get('id')
    experiment = Experiment.objects.filter(id=experiment_id)
    if not experiment.exists():
        return HttpResponse("ID not recognised")
    experiment = experiment[0]
    x_prime = getGuessesBasedOnPrime(experiment, 'X')
    j_prime = getGuessesBasedOnPrime(experiment, 'K')
    k_prime = getGuessesBasedOnPrime(experiment, 'J')

    x_scores, x_labels, x_percent = getChartData(x_prime)
    j_scores, j_labels, j_percent = getChartData(j_prime)
    k_scores, k_labels, k_percent = getChartData(k_prime)


    chartsData = list()

    x_info = {
        'title': "X Prime",
        'data': x_scores,
        'labels': x_labels,
        'percent': x_percent
    }
    chartsData.append(x_info)

    j_info = {
        'title': "J Prime",
        'data': j_scores,
        'labels': j_labels,
        'percent': j_percent
    }
    chartsData.append(j_info)

    k_info = {
        'title': "K Prime",
        'data': k_scores,
        'labels': k_labels,
        'percent': k_percent
    }
    chartsData.append(k_info)

    sampleChartsData = [{
        'title': "X Prime",
        'data': [124, 259],
        'labels': ["Correct", "Incorrect"],
        'percent': 32.38
    },
    {
        'title': "J Prime",
        'data': [89, 174],
        'labels': ["Correct", "Incorrect"],
        'percent': 33.84
    },
    {
        'title': "K Prime",
        'data': [35, 23],
        'labels': ["Correct", "Incorrect"],
        'percent': 60.34
    }



    ]
    
    return chartsData


def dataAnalysis(request):    
    experiment_id = request.GET.get('id')
    experiment = Experiment.objects.filter(id=experiment_id)
    if not experiment.exists():
        return HttpResponse("ID not recognised")
    experiment = experiment[0]

    context = {
        'id': experiment_id,
        'chartsData': getChartDataContext(request)
    }



    return render(request, "ResearcherPages/dataAnalysis.html", context)


def deleteExperiment(request):
    experiment_id = request.GET.get('id')
    experiment = Experiment.objects.filter(id=experiment_id)
    if not experiment.exists():
        return HttpResponse("ID not recognised")
    experiment = experiment[0]
    if request.user != experiment.user_source:
        return HttpResponse("You do not have permission to delete this experiment")
    experiment.delete()
    return redirect('listExperiments')

def deleteAudio(request):
    audio_id = request.GET.get('id')
    audio = Word.objects.filter(id=audio_id)
    if not audio.exists():
        return HttpResponse("ID not recognised")
    audio = audio[0]
    if request.user != audio.user_source:
        return HttpResponse("You do not have permission to delete this experiment")
    audio.delete()
    return redirect('showAudios')

def makeCSVforSurveyRound(survey_round):
    header = ['USER ID']
    survey = survey_round.survey
    researcher_id = survey_round.user_source.id

    surveyQs = SurveyQuestion.objects.filter(survey=survey).order_by('questionNumber')
    usersData = {}
    for q in surveyQs:
        header.append(str(q.questionText))
        ansOfQ = SurveyAnswer.objects.filter(surveyQuestion=q)
        for ans in ansOfQ:
            user = ans.user_source
            if str(user.id) in usersData:
                usersData[str(user.id)].append(ans.answer)
            else:
                usersData[str(user.id)] = [str(user.id), ans.answer]
    data = list()
    for user in usersData.values():
        data.append(user)
    
    fileName = str(researcher_id) + "/" + "SurveyRound" + str(survey_round.id) + ".csv"
    fullFile = os.path.join(settings.MEDIA_ROOT, fileName)
    with open(fullFile, 'w', encoding='UTF8', newline='') as f:

        writer = csv.writer(f)

        writer.writerow(header)

        for row in data:
            writer.writerow(row)

    return fullFile

def makeCSVforAudioRound(audio_round):
    pairGuessesQuery = UserPairGuess.objects.all()
    researcher_id = audio_round.user_source.id
    pairGuesses = list()
    for guessQuery in pairGuessesQuery:
        if guessQuery.associated_word_round.associated_audio_round == audio_round:
            pairGuesses.append(guessQuery)
    data = list()
    for guess in pairGuesses:
        pair = guess.pair
        word1 = pair.audio1.word
        word2 = pair.audio2.word
        answer = guess.answer
        userID = guess.associated_word_round.for_user.id
        prime = guess.prime
        pairList = [userID, word1.lower(), word2.lower(), answer.lower(), prime]
        data.append(pairList)
    
    header = ['USER ID', 'WORD ONE', 'WORD TWO', 'GUESS', 'PRIME']

    fileName = str(researcher_id) + "/" + "AudioRound" + str(audio_round.id) + ".csv"
    fullFile = os.path.join(settings.MEDIA_ROOT, fileName)
    with open(fullFile, 'w', encoding='UTF8', newline='') as f:

        writer = csv.writer(f)

        writer.writerow(header)

        for row in data:
            writer.writerow(row)

    return fullFile


def makeCSVforImageRound(image_round):	
    header = ['USER ID']	
    survey = image_round.survey	
    researcher_id = image_round.user_source.id	
    surveyQs = SurveyQuestion.objects.filter(survey=survey).order_by('questionNumber')	
    usersData = {}	
    for q in surveyQs:	
        header.append(str(q.questionText))	
        ansOfQ = SurveyAnswer.objects.filter(surveyQuestion=q)	
        for ans in ansOfQ:	
            user = ans.user_source	
            if str(user.id) in usersData:	
                usersData[str(user.id)].append(ans.answer)	
            else:	
                usersData[str(user.id)] = [str(user.id), ans.answer]	
    data = list()	
    for user in usersData.values():	
        data.append(user)	
    	
    fileName = str(researcher_id) + "/" + "Image" + str(image_round.id) + ".csv"	
    fullFile = os.path.join(settings.MEDIA_ROOT, fileName)	
    with open(fullFile, 'w', encoding='UTF8', newline='') as f:	
        writer = csv.writer(f)	
        writer.writerow(header)	
        for row in data:	
            writer.writerow(row)	
    return fullFile



def downloadData(request):
    experiment_id = request.GET.get('id')
    experiment = Experiment.objects.filter(id=experiment_id)
    if not experiment.exists():
        return HttpResponse("ID not recognised")
    experiment = experiment[0]
    createPath(os.path.join(settings.MEDIA_ROOT, str(experiment.user_source.id)))
    audioRounds = AudioRound.objects.filter(experiment=experiment)
    a_files = list()
    for audioR in audioRounds:
        f = makeCSVforAudioRound(audioR)
        a_files.append(f)

    surveyRounds = SurveyRound.objects.filter(experiment=experiment)
    for surveyR in surveyRounds:
        f = makeCSVforSurveyRound(surveyR)
        a_files.append(f)

    imageRounds = ImageRound.objects.filter(experiment=experiment)
    for imageR in imageRounds:
        f = makeCSVforImageRound(imageR)
        a_files.append(f)

    
    fileName = str(experiment.user_source.id) + "/" + "Experiment" + str(experiment.id) + ".xlsx"
    filePath = os.path.join(settings.MEDIA_ROOT, fileName)
    writer = pd.ExcelWriter(os.path.join(settings.MEDIA_ROOT, fileName), engine='xlsxwriter')

    for a_file in a_files:
        df = pd.read_csv(a_file)
        df.to_excel(writer, sheet_name=os.path.basename(a_file))

    writer.save()

    # Open the file for reading content
    path = open(filePath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filePath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % fileName
    # Return the response value
    return response



def userResults(request):
    experiment_id = request.GET.get('id')
    experiment = Experiment.objects.filter(id=experiment_id)
    if not experiment.exists():
        return HttpResponse("ID not recognised")
    experiment = experiment[0]
    userWordRounds = UserWordRound.objects.filter(experiment=experiment, for_user=request.user).order_by('id')
    dataContent = list()
    roundNum = 0
    for wordRound in userWordRounds:
        pairsInfo = list()
        userPairGuesses = UserPairGuess.objects.filter(associated_word_round=wordRound)
        total = len(userPairGuesses)
        correct = 0
        for guess in userPairGuesses:
            pair = guess.pair
            word1 = pair.audio1.word
            word2 = pair.audio2.word
            answer = guess.answer
            if word2.lower() == answer.lower():
                correct += 1
            pairInfo = [word1.lower, word2.lower, answer]
            pairsInfo.append(pairInfo)
        percent = 0.0
        if total > 0:
            percent = round((correct / total) * 100, 2)

        roundNum += 1
        roundName = "Round " + str(roundNum)
        dataContent.append([roundName, pairsInfo, correct, total, percent])

    context = {
        "object_list": dataContent,
        "id": experiment_id
    }
    
    return render(request, "userResults.html", context)




def detect_leading_silence(sound, silence_threshold=-40.0, chunk_size=10):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0 # ms

    assert chunk_size > 0 # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

def trimAudio(request):

    sound = AudioSegment.from_wav(request.FILES['file'])
    print("LENGTH OF SOUND", len(sound))
    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())
    duration = len(sound) 
    trimmed_sound = sound[start_trim - 20:duration-end_trim+20]
    print("NOW", len(trimmed_sound))
    user_id = request.user.id
    try:
        createPath(os.path.join(settings.MEDIA_ROOT, str(user_id)))
        createPath(os.path.join(settings.MEDIA_ROOT, str(user_id), "trimmedSounds"))
    except:
        print("Error creating paths in getTrimmedAudio() in views.py")
    file_location = getTrimmedAudio(user_id)
    file_handle = trimmed_sound.export(file_location, format="wav",)
    return redirect('uploadAudio')