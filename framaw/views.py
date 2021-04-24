from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from .models import *


def index(request):
    context = {
        'dirs': Directory.objects.all(),
        'files': File.objects.all()
    }
    return render(request, 'framaw/index.html', context)


def new_file(request):
    context ={'dirs': Directory.objects.all()}
    return render(request, 'framaw/new_file.html', context)


def create_file(request):
    filename = request.POST.get('name')
    description = request.POST.get('description')
    parent_dir = Directory.objects.get(id=request.POST.get('parent_dir'))
    content = request.POST.get('content')

    new_file = File(name=filename, description=description, directory=parent_dir, content=content)

    new_file.save()

    return HttpResponse(filename + " " + description + " " + parent_dir.name + " " + content)