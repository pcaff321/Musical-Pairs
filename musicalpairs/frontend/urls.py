from django.urls import path, include
from .views import index, app

urlpatterns = [
    path('', app, name='experimentPage'),
    path('', app, name='playExperiment'),
    path('create', app),
    path('join', app),
    path('survey', app),
    path('survey/<str:roomCode>', app, name='surveyPage'),
    path('survey2', app),
    path('room/<str:roomCode>', app),
    path('formtest', app)
]
