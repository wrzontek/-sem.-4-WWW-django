from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .models import *


def index(request):
    if request.user.is_authenticated:
        context = {
            'dirs': Directory.objects.all().filter(valid=True, owner=request.user),
            'files': File.objects.all().filter(valid=True, owner=request.user),
            'display_content': "",
        }
        return render(request, 'framaw/index.html', context)
    else:
        if request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("invalid username or password")
        else:
            return login_page(request)


def login_page(request):
    logout(request)
    return render(request, 'framaw/login_page.html', {})


def new_file(request):
    context ={'dirs': Directory.objects.all().filter(valid=True, owner=request.user)}
    return render(request, 'framaw/new_file.html', context)


# def save_file_content(name, f):
#     with open('some/file/name.txt', 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)
#
#
# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             filename = request.POST.get('name')
#             description = request.POST.get('description')
#             parent_dir = Directory.objects.get(id=request.POST.get('parent_dir'))
#             owner = User.objects.get(username=request.POST.get('owner'))
#             content = request.FILES.get('file')
#
#             new_file = File(name=filename, description=description, owner=owner, directory=parent_dir, content=content)
#
#             new_file.save()
#
#             return HttpResponseRedirect('/success/url/')
#
#     return index(request)


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
    context ={'dirs': Directory.objects.all().filter(valid=True, owner=request.user)}
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


def delete_file(request):
    context = {'files': File.objects.all().filter(valid=True, owner=request.user)}
    return render(request, 'framaw/delete_file.html', context)


def do_delete_file(request):
    name = request.POST.get('name')
    file = File.objects.get(name=name)
    file.delete()

    return HttpResponseRedirect(reverse('index'))


def delete_dir(request):
    context = {'dirs': Directory.objects.all().filter(valid=True, owner=request.user)}
    return render(request, 'framaw/delete_dir.html', context)


def do_delete_dir(request):
    name = request.POST.get('name')
    dir_to_delete = Directory.objects.get(name=name)
    dir_to_delete.delete()

    return HttpResponseRedirect(reverse('index'))


def display_file(request):
    file = File.objects.get(name=request.GET.get('name'))
    context = {
        'dirs': Directory.objects.all().filter(valid=True, owner=request.user),
        'files': File.objects.all().filter(valid=True, owner=request.user),
        'display_content': file.content,
    }
    return render(request, 'framaw/index.html', context)