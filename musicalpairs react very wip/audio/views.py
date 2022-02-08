from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import AudioForm, ResearcherSignUpForm, ExperimenteeSignUpForm
from .models import User, Survey
from .audio_manipulation import combineAudios
from .serializers import Audio_serializer, SurveySerializer, CreateSurveySerializer
from rest_framework.renderers import JSONRenderer
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response



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
    return render(request, 'login.html')


def survey_view(request):
    return render(request, 'mainsurvey.html')


class SurveyView(generics.ListAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

class GetRoomView(APIView):
    serializer_class = SurveySerializer
    lookup_url_kwarg = 'code'

    def get(self, request, format=None):
        code = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room = Survey.objects.filter(code=code)
            if len(room) > 0:
                data = SurveySerializer(room[0]).data
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'Bad Request': 'Code paramater not found in request'}, status=status.HTTP_400_BAD_REQUEST)


class CreateSurveyView(APIView):
    serializer_class = CreateSurveySerializer
    def post(self, request, format="None"):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            round_count = serializer.data.get("round_count")
            round_list = serializer.data.get("round_list")
            host = self.request.session.session_key
            survey = Survey(host=host, round_count = round_count,
            round_list = "placeholder")
            survey.save()

            return Response(SurveySerializer(survey).data, status=status.HTTP_201_CREATED)
            



class experimentee_signup(generics.CreateAPIView):
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


class researcher_signup(generics.CreateAPIView):
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
