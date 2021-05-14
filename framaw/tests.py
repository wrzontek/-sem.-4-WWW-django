from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.utils import timezone

from .models import *


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