from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import Audio_store_view, listExperiments, showAudios, createExperiment, createExperiment_POST, \
    main, roundTest, showAudios, playAudioFile, prevRoundPage, nextRoundPage, loginView, experimentee_signup, \
        researcher_signup, logout_view, ajaxTest,createPostTest, SurveyView, CreateSurveyView, GetRoomView, publish,\
            showResults, answerQuestion_POST, editExperiment
from .api import PostAnswer, addAnswer, showAnswers


urlpatterns = [
    path('survey', SurveyView.as_view(), name='survey'),
    path('createsurvey', CreateSurveyView.as_view(), name='createsurvey'),
    path('get-room', GetRoomView.as_view(), name='get-room'),
    path('uploadAudio/', Audio_store_view, name='uploadAudio'),
    path('playAudio/', playAudioFile, name='playAudio'),
    path('showAudios/', showAudios, name='showAudios'),
    path('showAnswers/', showAnswers, name='showAnswers'),
    path('answerQuestion_POST/', answerQuestion_POST, name='answerQuestion_POST'),
    path('listExperiments/', listExperiments, name='listExperiments'),
    path('editExperiment/', editExperiment, name='editExperiment'),
    path('showResults/', showResults, name='showResults'),
    path('login/', loginView, name='login'),
    path('create_post/', createPostTest, name='create_post'),
    path('ajaxTest/', ajaxTest),
    path('logout/', logout_view, name='logout'),
    path('createExperiment/', createExperiment, name='createExperiment'),
    path('postExperiment/', createExperiment_POST, name='postExperiment'),
    path('playRoundTest/', roundTest, name='playRoundTest'),
    path('prevRound/', prevRoundPage, name='prevRound'),
    path('nextRound/', nextRoundPage, name='nextRound'),
    path('postAnswer/', PostAnswer, name='postAnswer'),
    path('addAnswer/', addAnswer, name='addAnswer'),
    path('signup/experimentee/', experimentee_signup.as_view(), name='experimentee_signup'),
    path('signup/researcher/', researcher_signup.as_view(), name='researcher_signup'),
    path('publish/', publish, name="publish")
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
