from django.shortcuts import render, redirect

# Create your views here.
def index(request, *args, **kwargs):
    return render(request, 'frontend/index.html')

def app(request, *args, **kwargs):
    return render(request, 'frontend/app.html')

def home(request):
    return redirect('home')

# def survey(request, *args, **kwargs):
#     return render(request, 'frontend/survey.html')
