from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import AudioForm, ResearcherSignUpForm, ExperimenteeSignUpForm
from .models import Survey, User, set_file_name, Audio_store, Word, Experiment, Page, SurveyRound, AudioRound, TextRound, SurveyQuestion, SurveyAnswer
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

def showAnswers(request):
    audios_of_user = SurveyAnswer.objects.all()
    context = {
        "object_list": audios_of_user
    }
    return render(request, 'showAnswers.html', context)

def addAnswer(request):
    surveyID = SurveyQuestion.objects.all()[0].id
    experimentID = Experiment.objects.all()[0].id

    context = {
        "surveyID": surveyID,
        "experimentID": experimentID
    }
    return render(request, 'publishAnswerTest.html', context)



def PostAnswer(request):
    if request.method == 'POST':
        surveyID = request.POST.get('surveyID')
        experimentID = request.POST.get('experimentID')
        answer = request.POST.get('answer')
        user = request.user

        experiment = Experiment.objects.filter(id=experimentID)[0]
        survey = SurveyQuestion.objects.filter(id=surveyID)[0]

        answerInstance = SurveyAnswer(surveyQuestion=survey, experiment=experiment, user_source=user, answer=answer)
        answerInstance.save()

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
