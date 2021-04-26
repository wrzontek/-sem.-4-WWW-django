import io

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


def parse_file_content(content, file):
    buf = io.StringIO(content)
    frama_block = False
    line_number = 0
    have_line = False
    keywords = ["predicate", "requires", "ensures", "loop invariant", "loop variant", "assert", "assumes"]
    line = ""

    while True:
        if not have_line:
            line = buf.readline()
            line_number += 1
        if len(line) == 0:
            break

        have_line = False

        if "//@" in line:
            new_file_section = FileSection(file=file, line_number=line_number, content=line)
            new_file_section.save()  # TODO category(keyword), status, data
            frama_block = False

        else:
            if "/*@" in line:
                frama_block = True
            elif "@" in line and "*/" in line:
                frama_block = False

            if frama_block:
                content = ""
                cont = True
                fs_line_number = line_number
                while cont:     # kończymy sekcję gdy napotkamy kolejną lub koniec bloku
                    content += line
                    line = buf.readline()
                    line_number += 1

                    if len(line) == 0:
                        break
                    if "@" in line and "*/" in line:
                        have_line = True
                        frama_block = False
                        cont = False
                    else:
                        for keyword in keywords:
                            if keyword in line:
                                have_line = True
                                cont = False
                                break

                new_file_section = FileSection(file=file, line_number=fs_line_number, content=content)
                new_file_section.save()  # TODO category(keyword), status, data

    return


def create_file(request):
    filename = request.POST.get('name')
    description = request.POST.get('description')
    parent_dir = Directory.objects.get(id=request.POST.get('parent_dir'))
    owner = User.objects.get(username=request.POST.get('owner'))
    content = request.POST.get('content')

    new_file = File(name=filename, description=description, owner=owner, directory=parent_dir, content=content)
    new_file.save()

    parse_file_content(content, new_file)

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
    file.valid = False
    file.save()
    return HttpResponseRedirect(reverse('index'))


def delete_dir(request):
    context = {'dirs': Directory.objects.all().filter(valid=True, owner=request.user)}
    return render(request, 'framaw/delete_dir.html', context)


def recursive_delete_dir(dir_name):
    dir_to_delete = Directory.objects.get(name=dir_name)
    if dir_to_delete.valid:
        for file in File.objects.all():
            if file.directory == dir_to_delete:
                file.valid = False
                file.save()

        for directory in Directory.objects.all():
            if directory.parent_dir == dir_to_delete and directory.valid:
                recursive_delete_dir(directory.name)

    dir_to_delete.valid = False
    dir_to_delete.save()


def do_delete_dir(request):
    dir_name = request.POST.get('name')
    recursive_delete_dir(dir_name)

    return HttpResponseRedirect(reverse('index'))


def display_file(request):
    file = File.objects.get(name=request.GET.get('name'))
    context = {
        'dirs': Directory.objects.all().filter(valid=True, owner=request.user),
        'files': File.objects.all().filter(valid=True, owner=request.user),
        'display_content': file.content,
    }
    return render(request, 'framaw/index.html', context)