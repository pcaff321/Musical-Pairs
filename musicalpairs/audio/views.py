from audioop import reverse

from django.db import models
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from pyexpat.errors import messages

from . import email_utility, validation_utility
from .forms import AudioForm, ResearcherSignUpForm, ExperimenteeSignUpForm, PublishForm
from .models import User, Experiment
from .audio_manipulation import combineAudios
from .serializers import Audio_serializer
from rest_framework.renderers import JSONRenderer
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView




# Create your views here.

def main(request):
    return HttpResponse("Test")
    

@login_required
def Audio_store(request):
    if request.method == 'POST': 
        form = AudioForm(request.POST,request.FILES or None) 
        if form.is_valid(): 
            form = form.save() 
            combineAudios()
            serializer = Audio_serializer(form)
            json = JSONRenderer().render(serializer.data)
            return HttpResponse(str(json))
    else: 
        form = AudioForm() 
    return render(request, 'aud.htm', {'form' : form}) 


def playAudioFile(request):
    url = settings.MEDIA_URL + "user_efaefa/efaefa.wav"
    return render(request, 'playAudio.html', {'link': url })

def loginView(request):
    if request.method == 'POST':
        post_data = request.POST.copy()

        return render(request, 'login.html')
    else:
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
                """send_mail(subject, body, "osullivanc3@gmail.com", emails)"""
                message = "Message sent successfully"
            form = PublishForm()
            return render(request, 'publish.html', {'form':form, 'message': message})
    else:
        form = PublishForm()
        message = ""
    return render(request, 'publish.html', {'form' : form, 'message': message})
    
def logout_view(request):
    logout(request)
    return redirect("/signup/experimentee/")

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
