import re
from json import JSONDecodeError

import ldap
from django.shortcuts import render

from firstapp.directory_api_function import create_user
from firstapp.getfunctions import connect_to_ldap


class Data:
    name = str
    surname = str
    patronymic = str
    login = str
    password = str


def activation(request):
    if request.method == "GET":
        return render(request, "activation/activation.html")
    if request.method == "POST":
        ad = connect_to_ldap(request)
        results = ad.search("dc=kspu,dc=ru", ldap.SCOPE_SUBTREE,
                            'passportNumber=' + request.POST.get("passport_series") + " " + request.POST.get(
                                "passport_number"))
        while ad:
            result_type, result_data = ad.result(results, 0)
            if result_data:
                if re.findall("(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[а-яА-Я]).{6,20}$",
                              request.POST.get("password")):
                    if (result_data[0][1]['uid'][0].decode() == request.POST.get("login")) & (result_data[0][1].get('userPassword') is None):
                        data = Data
                        data.name = result_data[0][1]['givenName'][0].decode()
                        data.surname = result_data[0][1]['sn'][0].decode()
                        data.patronymic = result_data[0][1]['initials'][0].decode()
                        data.login = result_data[0][1]['uid'][0].decode()
                        data.password = request.POST.get("password")
                        try:
                            code = create_user(data)
                        except JSONDecodeError:
                            return render(request, "error.html",
                                          {"error": "JSONDecodeError, вероятнее всего сервис API временно "
                                                    "недоступен."})
                        if code['status_code'] == 201:
                            add_pass = [(ldap.MOD_REPLACE, 'userPassword', [bytes(request.POST.get("password").encode())]),
                                        (ldap.MOD_REPLACE, 'employeeNumber', [bytes(request.POST.get("number").encode())])]
                            ad.modify_s(result_data[0][0], add_pass)
                            ad.unbind()
                            return render(request, "activation/activation.html", {"message": "Активация прошла успешно"})
                        else:
                            return render(request, "activation/activation.html",
                                          {"message": "Ошибка Yandex"})

                    elif result_data[0][1]['userPassword'][0].decode() is not None:
                        return render(request, "activation/activation.html", {"message": "Пользователь уже активирован"})
                    else:
                        return render(request, "activation/activation.html", {"message": "Логин не подходит"})
                else:
                    ad.unbind()
                    return render(request, "activation/activation.html", {"message": "Пароль не подходит"})
            else:
                ad.unbind()
                return render(request, "activation/activation.html",
                              {"message": "По серии и номеру паспорта студент не найден"})


def notes(request):
    return render(request, "activation/notes.html")
