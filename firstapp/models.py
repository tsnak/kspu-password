# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models


# Create your models here.
class Person(models.Model):
    username = models.CharField(max_length=256)
    email = models.CharField(max_length=256)


class Admin(models.Model):
    username = models.CharField(max_length=256)
    right = models.TextField()
    fullname = models.TextField()


class PasswordRecoveryData(models.Model):
    secret_key = models.CharField(max_length=20)
    username = models.CharField(max_length=256)
    date = models.DateTimeField(default=datetime.datetime.now(datetime.timezone.utc))


class RegistrationData(models.Model):
    name = models.TextField()
    surname = models.TextField()
    patronymic = models.TextField()
    login = models.TextField()
    position = models.TextField()
    number = models.TextField()
    year = models.TextField()
    password = models.TextField()
    path = models.TextField()


class RegistrationAdmin(models.Model):
    fullname = models.TextField()
    username = models.TextField()
