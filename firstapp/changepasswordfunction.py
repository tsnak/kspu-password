import re
from json import JSONDecodeError

import ldap
from django.shortcuts import render

from firstapp.directory_api_function import update_user_password
from firstapp.getfunctions import connect_to_ldap


def change_password_function(request, username, password):
    if re.findall("(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[а-яА-Я]).{6,20}$", request.POST.get("new_password")):
        ad = connect_to_ldap(request)
        results = ad.search("dc=kspu,dc=ru", ldap.SCOPE_SUBTREE, 'uid=' + username)
        while ad:
            result_type, result_data = ad.result(results, 0)
            if result_data:
                try:
                    yandex = update_user_password(username, password)
                except JSONDecodeError:
                    return "JSONDecodeError, вероятнее всего сервис API Yandex временно "\
                                            "недоступен."
                if yandex['status_code'] == 422:
                    ad.unbind()
                    if yandex['text']['message'] == 'Password equals previous':
                        return "Пароль совпадает с предыдущим"
                    else:
                        return "Ошибка при вводе пароля"
                if yandex['status_code'] == 200 or yandex['status_code'] == 404:
                    password_value = bytes(password.encode())
                    add_pass = [(ldap.MOD_REPLACE, 'userPassword', [password_value])]
                    ad.modify_s(result_data[0][0], add_pass)
                ad.unbind()
                return 0
            else:
                break
    else:
        return "Введённый новый пароль не подходит по требованиям (6-20 символов, как минимум одна цифра, " \
               "одна большая и одна маленькая буква) "
