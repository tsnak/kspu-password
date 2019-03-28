import datetime
import re

import ldap
from django.http import HttpResponseRedirect
from django.shortcuts import render

from firstapp.getfunctions import connect_to_ldap, get_cn
from firstapp.models import RegistrationData


class Faculties:
    def __init__(self, name, link):
        self.name = name
        self.link = link


def registration(request, path="ou=kspu,dc=kspu,dc=ru"):
    faculty = [Faculties]
    ad = connect_to_ldap(request)
    if request.method == "GET":
        results = ad.search(path, ldap.SCOPE_ONELEVEL, 'objectClass=organizationalUnit')
        while ad:
            result_type, result_data = ad.result(results, 0)
            if result_data:
                try:
                    faculty.append(Faculties(result_data[0][1].get('description')[0].decode(),
                                             result_data[0][0]))
                except:
                    continue
            else:
                break

        if len(faculty) != 1:
            return render(request, "registration/registration.html", {'faculties': faculty})
        else:
            return render(request, "registration/new_user_creation.html")
    if request.method == "POST":
        if request.POST.get("password") != request.POST.get("repeat_new_password"):
            return render(request, "registration/new_user_creation.html", {'message': 'пароли не совпадают'})
        if get_cn(request, request.POST.get("login")) is not None:
            return render(request, "registration/new_user_creation.html", {'message': 'указаный логин уже занят'})
        if re.findall("(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[а-яА-Я]).{6,20}$",
                      request.POST.get("password")):
            data = RegistrationData()
            data.name = request.POST.get("name")
            data.surname = request.POST.get("surname")
            data.patronymic = request.POST.get("patronymic")
            data.login = request.POST.get("login")
            data.number = request.POST.get("number")
            data.position = request.POST.get("position")
            data.password = request.POST.get("password")
            data.year = request.POST.get("year")
            data.path = path
            data.save()
            return render(request, "registration/sucessful_registration.html")
        else:
            return render(request, "registration/new_user_creation.html", {'message': "Введённый новый пароль не подходит по требованиям (6-20 символов, как минимум одна цифра, одна большая и одна маленькая буква)"})
    ad.unbind()
