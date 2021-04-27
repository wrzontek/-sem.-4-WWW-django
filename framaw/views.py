import io
from pathlib import Path

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import subprocess, os
from .models import *

RTE = False
props = []
provers = ["alt-ergo", "z3", "cvc4"]


def index(request):
    if request.user.is_authenticated:
        context = {
            'dirs': Directory.objects.all().filter(valid=True, owner=request.user),
            'files': File.objects.all().filter(valid=True, owner=request.user),
            'selected_file': "", 'focus_content': "", 'result_summary': "", 'provers': provers,
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
    context = {'dirs': Directory.objects.all().filter(valid=True, owner=request.user)}
    return render(request, 'framaw/new_file.html', context)


keywords = ["predicate", "requires", "ensures", "loop invariant",
            "loop variant", "assert", "assumes", "axiomatic"]


def describe_section(file_section, owner):
    for keyword in keywords:
        if keyword in file_section.content:
            category = SectionCategory(category=keyword, file_section=file_section)
            category.save()

    status = SectionStatus(status="unchecked", file_section=file_section)
    status_data = StatusData(data="", user=owner, file_section=file_section)

    status.save()
    status_data.save()

    file_section.status_data = status_data
    file_section.section_category = category
    file_section.section_status = status

    file_section.save()

    return


def parse_file_content(content, file):
    buf = io.StringIO(content)
    frama_block = False
    line_number = 0
    have_line = False
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
                while cont:  # kończymy sekcję gdy napotkamy kolejną lub koniec bloku
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
                describe_section(new_file_section, file.owner)

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
    context = {'dirs': Directory.objects.all().filter(valid=True, owner=request.user)}
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
    args = ["frama-c", "-wp", "-wp-print", file.name]
    if 'prover' in request.GET and 'rte' in request.GET:
        args = ["frama-c", "-wp", "-wp-prover", request.GET['prover'], "-wp-rte", file.name]
    elif 'prover' in request.GET:
        args = ["frama-c", "-wp", "-wp-prover", request.GET['prover'], file.name]
    elif 'rte' in request.GET:
        args = ["frama-c", "-wp", "-wp-rte", file.name]

    f = open(file.name, "x")
    f.write(file.content)
    f.close()

    run = subprocess.run(args, capture_output=True, text=True)
    subprocess.run(["frama-c", "-wp", "-wp-log=r:result.txt", file.name], capture_output=True, text=True)
    f_results = open("result.txt", "r")

    context = {
        'dirs': Directory.objects.all().filter(valid=True, owner=request.user),
        'files': File.objects.all().filter(valid=True, owner=request.user),
        'selected_file': file, 'focus_content': run.stdout, 'result_summary': f_results.read(),
        'provers': provers,
    }

    f_results.close()
    os.remove(file.name)
    os.remove("result.txt")

    return render(request, 'framaw/index.html', context)

