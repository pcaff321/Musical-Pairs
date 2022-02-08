from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import Audio_store, main, playAudioFile, \
loginView, experimentee_signup, researcher_signup, logout_view, survey_view, SurveyView, CreateSurveyView, GetRoomView


urlpatterns = [
    path('survey', SurveyView.as_view()),
    path('createsurvey', CreateSurveyView.as_view()),
    path('get-room', GetRoomView.as_view()),
    path('uploadAudio/', Audio_store),
    path('playAudio/', playAudioFile),
    path('login/', loginView),
    path('logout/', logout_view),
    path('survey/', survey_view),
    path('signup/experimentee/', experimentee_signup.as_view(), name='experimentee_signup'),
    path('signup/researcher/', researcher_signup.as_view(), name='researcher_signup')
]+ static(settings.MEDIA_URL,documecnnt_root=settings.MEDIA_ROOT)
