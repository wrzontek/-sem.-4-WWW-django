from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import *
from .views import *


class ModelTests(TestCase):

    def test_create_and_cascade_delete(self):
        user = User(username="test_usr", password="examplepassword123124$")
        dir = Directory(name="test_dir", description="test_desc", owner=user)
        file = File(name="test_file", description="test_desc", owner=dir.owner, directory=dir, content="łubudubu")
        fs = FileSection(file=file, line_number=0, content=file.content)

        sc = SectionCategory(category="fake_category", file_section=fs)
        status = SectionStatus(status="fake_status", file_section=fs)
        status_data = StatusData(data="fake_data", user=file.owner, file_section=fs)

        user.save()
        dir.save()
        file.save()
        fs.save()

        self.assertEqual(dir.owner, user)
        self.assertEqual(file.owner, user)
        self.assertEqual(status_data.user, user)

        dir.delete()

        self.assertEqual(len(Directory.objects.all()), 0)
        self.assertEqual(len(File.objects.all()), 0)
        self.assertEqual(len(FileSection.objects.all()), 0)
        self.assertEqual(len(SectionCategory.objects.all()), 0)
        self.assertEqual(len(SectionStatus.objects.all()), 0)
        self.assertEqual(len(StatusData.objects.all()), 0)
        self.assertEqual(len(User.objects.all()), 1)


class ViewsTests(TestCase):

    def test_no_logon(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_logon_invalid(self):
        c = Client()
        response = c.post('/framaw/', {'username': 'john', 'password': 'smith'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"invalid username or password")

    def test_logon_valid(self):
        c = Client()
        User.objects.create_user(username="usr", password="password123").save()
        response = c.post('/framaw/', {'username': 'usr', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)

    def test_new_file(self):
        c = Client()
        User.objects.create_user(username="usr", password="password123").save()
        response = c.post('/framaw/', {'username': 'usr', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        response = c.post('/framaw/new_file/')
        self.assertEqual(response.status_code, 200)

    def test_describe_section(self):
        user = User(username="test_usr", password="examplepassword123124$")
        dir = Directory(name="test_dir", description="test_desc", owner=user)
        file = File(name="test_file", description="test_desc", owner=dir.owner, directory=dir, content="łubudubu")

        user.save()
        dir.save()
        file.save()

        fs = FileSection(file=file, line_number=0,
                         content="  @   ensures \\result >= 0 ==> t[\\result] == v;\r\n  @ behavior failure:\r\n")
        fs.save()

        describe_section(fs, user)

        self.assertEqual(len(FileSection.objects.all()), 1)
        self.assertEqual(len(SectionCategory.objects.all()), 1)
        self.assertEqual(len(SectionStatus.objects.all()), 1)
        self.assertEqual(len(StatusData.objects.all()), 1)

        sc = SectionCategory.objects.all()[0]
        ss = SectionStatus.objects.all()[0]
        sd = StatusData.objects.all()[0]

        self.assertEqual(sc.category, "ensures")
        self.assertEqual(ss.status, "unchecked")
        self.assertEqual(sd.data, "")
