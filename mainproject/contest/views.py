from django.shortcuts import render,get_object_or_404
from .models import Contest

# Create your views here.

def home_view(request):
    return render(request, 'home.html')

def index_view(request):
    #retirve contest from database
    contests = Contest.objects.all()
    return render(request, 'contest/index.html', {'contests': contests})

def contest_view(request, id):
    contest = get_object_or_404(Contest, id=id)  # Fetch contest using ID
    return render(request, 'contest/contest.html', {'contest': contest})