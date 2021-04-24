from django.db import models
from django.utils import timezone


class User(models.Model):
    name = models.CharField(max_length=50, unique=True)
    login = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30)

    valid = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


# TODO te model.CASCADE wszędzie może do wymiany


class Directory(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, default="")
    creation_date = models.DateTimeField(default=timezone.now)
    parent_dir = models.ForeignKey('self', on_delete=models.CASCADE, default="", blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    valid = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, default="")
    creation_date = models.DateTimeField(default=timezone.now)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    content = models.CharField(max_length=3000, default="")

    valid = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class SectionCategory(models.Model):
    category = models.CharField(max_length=20)
    # TODO ^może nie char tylko jakiś wybór czy enum
    file_section = models.ForeignKey('FileSection', on_delete=models.CASCADE)

    valid = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)


class SectionStatus(models.Model):
    status = models.CharField(max_length=20)
    # TODO ^może nie char tylko jakiś wybór czy enum
    file_section = models.ForeignKey('FileSection', on_delete=models.CASCADE)

    valid = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)


class StatusData(models.Model):
    data = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_section = models.ForeignKey('FileSection', on_delete=models.CASCADE)

    valid = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)


class FileSection(models.Model):
    name = models.CharField(max_length=50, default="")
    description = models.CharField(max_length=200, default="")
    creation_date = models.DateTimeField()
    file = models.ForeignKey(File, on_delete=models.CASCADE)

    section_category = models.ForeignKey(SectionCategory, on_delete=models.CASCADE)
    section_status = models.ForeignKey(SectionStatus, on_delete=models.CASCADE)
    status_data = models.ForeignKey(StatusData, on_delete=models.CASCADE)

    valid = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)