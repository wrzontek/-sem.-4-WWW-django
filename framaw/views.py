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
    owner = User.objects.get(name=request.POST.get('owner'))
    content = request.POST.get('content')

    new_file = File(name=filename, description=description, owner=owner, directory=parent_dir, content=content)

    new_file.save()

    return HttpResponseRedirect(reverse('index'))


def new_directory(request):
    context ={'dirs': Directory.objects.all()}
    return render(request, 'framaw/new_directory.html', context)


def create_directory(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    owner = User.objects.get(name=request.POST.get('owner'))

    if request.POST.get('parent_dir') == "":
        parent_dir = ""
    else:
        parent_dir = Directory.objects.get(id=request.POST.get('parent_dir'))

    new_directory = Directory(name=name, description=description, owner=owner, parent_dir=parent_dir)

    new_directory.save()

    return HttpResponseRedirect(reverse('index'))