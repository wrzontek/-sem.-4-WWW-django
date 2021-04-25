from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .models import *


def index(request):
    if request.user.is_authenticated:
        context = {
            'dirs': Directory.objects.all().filter(valid=True),
            'files': File.objects.all().filter(valid=True)
        }
        return render(request, 'framaw/index.html', context)
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponse("invalid username or password")


def login_page(request):
    context = {}
    return render(request, 'framaw/login_page.html', context)


def new_file(request):
    context ={'dirs': Directory.objects.all()}
    return render(request, 'framaw/new_file.html', context)


def create_file(request):
    filename = request.POST.get('name')
    description = request.POST.get('description')
    parent_dir = Directory.objects.get(id=request.POST.get('parent_dir'))
    owner = User.objects.get(username=request.POST.get('owner'))
    content = request.POST.get('content')

    new_file = File(name=filename, description=description, owner=owner, directory=parent_dir, content=content)

    new_file.save()

    return HttpResponseRedirect(reverse('index'))


def new_directory(request):
    context ={'dirs': Directory.objects.all().filter(valid=True)}
    return render(request, 'framaw/new_directory.html', context)


def create_directory(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    owner = User.objects.get(username=request.POST.get('owner'))

    if request.POST.get('parent_dir') == "":
        created_directory = Directory(name=name, description=description, owner=owner)
    else:
        parent_dir = Directory.objects.get(id=request.POST.get('parent_dir'))
        created_directory = Directory(name=name, description=description, owner=owner, parent_dir=parent_dir)

    created_directory.save()

    return HttpResponseRedirect(reverse('index'))