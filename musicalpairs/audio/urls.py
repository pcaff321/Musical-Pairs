from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import Audio_store_view, main, showAudios, playAudioFile, loginView, experimentee_signup, researcher_signup, logout_view


urlpatterns = [
    path('uploadAudio/', Audio_store_view),
    path('playAudio/', playAudioFile),
    path('showAudios/', showAudios),
    path('login/', loginView),
    path('logout/', logout_view),
    path('signup/experimentee/', experimentee_signup.as_view(), name='experimentee_signup'),
    path('signup/researcher/', researcher_signup.as_view(), name='researcher_signup')
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
