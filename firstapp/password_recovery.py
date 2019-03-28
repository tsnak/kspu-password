import smtplib

from django.http import HttpResponseRedirect
from django.shortcuts import render
import datetime
import socket

from firstapp.changepasswordfunction import change_password_function
from firstapp.models import PasswordRecoveryData, Person
from firstapp.random_values import random_string


def forgot_password(request):
    try:
        s = smtplib.SMTP_SSL('smtps.kspu.ru')
    except socket.gaierror:
        return render(request, "error.html", {"error": "Socket GAIError"})
    try:
        s.login('mail-restore', 'Ze24YjTxBnwGS8OI')
    except smtplib.SMTPAuthenticationError:
        return render(request, "error.html", {"error": "SMTP authentification error"})
    if request.method == "POST":
        try:
            user = Person.objects.get(username=request.POST.get("name"))
        except Person.DoesNotExist:
            try:
                user = Person.objects.get(email=request.POST.get("name"))
            except Person.DoesNotExist:
                return render(request, "error.html", {"error": "Person doesn't exist"})
        key = random_string(20)
        data = PasswordRecoveryData()
        data.secret_key = key
        data.username = user.username
        data.save()
        s.sendmail('mail-restore@kspu.ru', [user.email],
                   ("Ваша ссылка: http://as.kspu.ru/password_recovery/" + key).encode('utf-8'))
        return render(request, "sent.html")
    return render(request, "forgot.html")


def password_recovery(request, secret_key):
    if request.method == "GET":
        try:
            user = PasswordRecoveryData.objects.get(secret_key=secret_key)
            if user.date + datetime.timedelta(minutes=7) < datetime.datetime.now(datetime.timezone.utc):
                user.delete()
                return render(request, "error.html")
        except PasswordRecoveryData.DoesNotExist:
            return render(request, "error.html", {"error": "Password recovery data doesn't exist"})
        return render(request, "recovery.html")
    if request.method == "POST":
        if request.POST.get("new_password") == request.POST.get("new_password_again"):
            try:
                user = PasswordRecoveryData.objects.get(secret_key=secret_key)
            except PasswordRecoveryData.DoesNotExist:
                return render(request, "error.html", {"error": "Password recovery data doesn't exist"})
            message = change_password_function(request, user.username, request.POST.get("new_password"))
            if message == 0:
                user.delete()
                return HttpResponseRedirect("/")
            else:
                return render(request, "error.html", {"error": message})