from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import AudioForm, ResearcherSignUpForm, ExperimenteeSignUpForm
from .models import User, Audio_store
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
    print("HERE")
    if request.method == 'POST':
        form = AudioForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()  
    else: 
        form = AudioForm() 
    return render(request, 'aud.htm', {'form' : form}) 



def playAudioFile(request):
    combineAudios()
    url = settings.MEDIA_URL + 'combinedAudio.wav'
    return render(request, 'playAudio.html', {'link': url })


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