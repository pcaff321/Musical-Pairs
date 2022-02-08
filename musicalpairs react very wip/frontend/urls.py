from django.urls import path, include
from .views import index, app

urlpatterns = [
    path('', app),
    path('create', app),
    path('join', app),
    path('survey', app),
    path('survey/<str:roomCode>', app),
    path('survey2', app),
    path('room/<str:roomCode>', app)
]
