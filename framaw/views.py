from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import *

def index(request):
    context = {
        'dirs': Directory.objects.all(),
        'files': File.objects.all()
    }
    return render(request, 'framaw/index.html', context)