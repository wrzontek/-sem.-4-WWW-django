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


class Directory(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, default="")
    creation_date = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    valid = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name