import datetime

from _ldap import ALREADY_EXISTS
from json import JSONDecodeError

from django.http import HttpResponseRedirect
from django.shortcuts import render

from firstapp.directory_api_function import create_user
from firstapp.getfunctions import connect_to_ldap
from firstapp.models import RegistrationData


def users_to_accept_list(request):
    if request.method == "GET":
        data = RegistrationData.objects.all()
        return render(request, "registration/users_to_accept_list.html", {"data": data})


def delete_user(request, id):
    user = RegistrationData.objects.get(id = id)
    user.delete()
    return HttpResponseRedirect("/accept_user")


def add_user(request, id):
    user = RegistrationData.objects.get(id=id)
    ad = connect_to_ldap(request)
    array = [
        ('objectclass', [bytes('top'.encode()),
                         bytes('person'.encode()),
                         bytes('organizationalPerson'.encode()),
                         bytes('inetOrgPerson'.encode()),
                         bytes('mailUser'.encode()),
                         bytes('InetQuota'.encode()),
                         bytes('userMailQuota'.encode())]),
        ('cn', [bytes(user.name.encode())]),
        ('displayName', [bytes((user.surname+user.name+user.patronymic).encode())]),
        ('sn', [bytes(user.surname.encode())]),
        ('givenName', [bytes(user.name.encode())]),
        ('initials', [bytes(user.patronymic.encode())]),
        ('mail', [bytes((user.login + "@kspu.ru").encode())]),
        ('uid', [bytes(user.login.encode())]),
        ('mailacceptinggeneralid', [bytes(user.login.encode())]),
        ('maildrop', [bytes(user.login.encode())]),
        ('title', [bytes(user.position.encode())]),
        ('employeeNumber', [bytes(user.number.encode())]),
        ('telexNumber', [bytes(str(datetime.datetime.now(datetime.timezone.utc)).encode())]),
        ('description', [bytes(" ".encode())]),
        ('roomNumber', [bytes(" ".encode())]),
        ('telephoneNumber', [bytes("+79504103422".encode())]),
        ('x121Address', [bytes(user.year.encode())]),
        ('Quota', [bytes("0".encode())]),
        ('mailQuota', [bytes("0".encode())]),
        ('userPassword', [bytes(user.password.encode())])
    ]
    try:
        ad.add_s("uid=" + user.login + "," + user.path, array)
    except ALREADY_EXISTS:
        return render(request, "error.html", {"error": "Уже есть в LDAP"})
    try:
        status = create_user(user)
    except JSONDecodeError:
        ad.delete("uid=" + user.login + "," + user.path)
        return render(request, "error.html", {"error": "JSONDecodeError, вероятнее всего сервис API временно "
                                                       "недоступен."})
    if status['status_code'] == 409:
        ad.delete("uid=" + user.login + "," + user.path)
        return render(request, "error.html", {"error": "Уже есть в Yandex"})
    if status['status_code'] == 403:
        ad.delete("uid=" + user.login + "," + user.path)
        return render(request, "error.html", {"error": "У пользователя или приложения нет прав на доступ к ресурсу, запрос отклонен."})
    if status['status_code'] == 422:
        ad.delete("uid=" + user.login + "," + user.path)
        return render(request, "error.html", {"error": "Ошибка валидации, запрос отклонен (например, выбранный логин уже занят)."})
    if status['status_code'] == 503:
        ad.delete("uid=" + user.login + "," + user.path)
        return render(request, "error.html", {"error": "Сервис API временно недоступен."})
    if status['status_code'] == 500:
        ad.delete("uid=" + user.login + "," + user.path)
        return render(request, "error.html", {"error": "Внутренняя ошибка сервиса. Попробуйте повторно отправить запрос через некоторое время."})
    user.delete()
    return HttpResponseRedirect("/accept_user")